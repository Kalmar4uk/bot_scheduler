import os
from datetime import datetime, timedelta

import asyncpg
from dotenv import load_dotenv

from bot.constants import STATUSES_FOR_REMINDERS
from bot.exceptions import (DoubleStore, ProblemConnectToDb,
                            ProblemToGetUpdateDataWithDB, ProblemToSaveInDB,
                            ReplyIsEmpty)
from bot.settings_logs import logger
from bot.utils import Store

load_dotenv()


async def connect_to_db():
    """Подключение к БД"""
    try:
        conn = await asyncpg.connect(
            database="storeopen",
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host="localhost",
            port="5432"
        )
    except Exception as e:
        logger.error(f"Возникла ошибка при подключении к БД: {e}")
        raise ProblemConnectToDb(error=str(e))
    return conn


async def create_to_db(message: list, chat_id: int):
    """Запись новых данных в БД"""
    store = Store.convertation_from_message(message=message, chat_id=chat_id)
    conn = await connect_to_db()
    try:
        async with conn.transaction():
            double_data = await conn.fetch(
                """
                SELECT sap_id, date_event
                FROM stores
                WHERE sap_id = $1 and date_event = $2
                """,
                store.sap_id, store.date
            )
            if double_data:
                raise DoubleStore()
            await conn.execute(
                """
                INSERT INTO stores (sap_id, date_event, chat_id, description)
                VALUES ($1, $2, $3, $4)
                """,
                store.sap_id, store.date, store.chat_id, store.description
            )
    except Exception as e:
        logger.error(f"Возникла ошибка при записи в БД: {e}")
        raise ProblemToSaveInDB(error=e)
    finally:
        await conn.close()


async def get_stores():
    """Получение магазинов из БД"""
    conn = await connect_to_db()
    date: datetime = datetime.now().date() + timedelta(days=5)
    try:
        async with conn.transaction():
            values = await conn.fetch(
                """
                SELECT id, sap_id, date_event, description, chat_id
                FROM stores
                WHERE date_event = $1
                """,
                date
            )
        logger.info("Получили данные из БД")
    except Exception as e:
        logger.error(f"Возникла ошибка при получении магазинов из БД: {e}")
        raise ProblemToGetUpdateDataWithDB(str(e))
    finally:
        await conn.close()

    return values


async def added_store_in_reminders_table(stores: list[Store], message_id: int):
    """Добавление магазина в таблицу reminders"""
    conn = await connect_to_db()
    try:
        for store in stores:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO reminders (
                    store_id, message_id, status, last_notified_data
                    )
                    VALUES ($1, $2, $3)
                    """,
                    store.id, message_id,
                    STATUSES_FOR_REMINDERS["cr"], datetime.now()
                )
        logger.info("Данные добавлены")
    except Exception as e:
        logger.error(f"Возникла ошибка при записи в БД: {e}")
        raise ProblemToSaveInDB(error=e)
    finally:
        await conn.close()


async def update_store_received_confirmation(message_id: int):
    """Обновление магазинов по которым получили подтверждение"""
    conn = await connect_to_db()
    try:
        async with conn.transaction():
            values = await conn.execute(
                """
                UPDATE reminders
                SET status = $1, last_notified_data = $2
                WHERE message_id = $3
                """,
                STATUSES_FOR_REMINDERS["cn"], datetime.now(), message_id
            )
            if int(values[-1]) == 0:
                logger.error(f"message_id {message_id} отсутствует в базе")
                raise ReplyIsEmpty(message_id=message_id)
    except ReplyIsEmpty:
        raise
    except Exception as e:
        logger.error(f"Возникла ошибка при обновлении магазинов: {e}")
        raise ProblemToGetUpdateDataWithDB(str(e))
    finally:
        await conn.close()


async def get_reminders_for_repeat():
    conn = await connect_to_db()
    try:
        async with conn.transaction():
            values = await conn.fetch(
                """
                SELECT
                s.id,
                s.sap_id,
                s.date_event,
                s.description,
                s.chat_id,
                r.message_id
                FROM stores s
                JOIN reminders r ON r.store_id = s.id
                WHERE r.status not in ($1, $2) and r.created_at < $3
                """,
                STATUSES_FOR_REMINDERS["cr"],
                STATUSES_FOR_REMINDERS["ex"],
                datetime.now()
            )
        logger.info("Получили данные из БД")
    except Exception as e:
        logger.error(f"Возникла ошибка при получении магазинов: {e}")
        raise ProblemToGetUpdateDataWithDB(str(e))
    finally:
        await conn.close()
    return values


async def update_reminders_for_repeat(message_ids: list[int]):
    """Обновление статуса повторно напоминания"""
    conn = await connect_to_db()
    try:
        async with conn.transaction():
            await conn.execute(
                """
                UPDATE reminders
                SET status = $1, last_notified_data = $2
                WHERE message_id = ANY($3)
                """,
                STATUSES_FOR_REMINDERS["rp"], datetime.now(), (message_ids,)
            )
    except Exception as e:
        logger.error(f"Возникла ошибка при обновлении магазинов: {e}")
        raise ProblemToGetUpdateDataWithDB(str(e))
    finally:
        await conn.close()


async def messages_to_expired():
    """Перевод напоминаний в просроченные"""
    conn = await connect_to_db()
    try:
        async with conn.transaction():
            await conn.execute(
                """
                UPDATE reminders
                SET status = $1, last_notified_data = $2
                WHERE store_id in (
                SELECT s.id
                FROM stores s
                JOIN reminders r ON s.id = r.store_id
                WHERE s.date_event < $2 and r.status != $4
                )
                """,
                STATUSES_FOR_REMINDERS["ex"],
                datetime.now(),
                STATUSES_FOR_REMINDERS["cn"]
            )
            logger.info("Напоминания переведены в просроченные")
    except Exception as e:
        logger.error(f"Возникла ошибка при обновлении магазинов: {e}")
        raise ProblemToGetUpdateDataWithDB(str(e))
    finally:
        await conn.close()
