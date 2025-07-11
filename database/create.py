from datetime import datetime

from dotenv import load_dotenv

from bot.constants import STATUSES_FOR_REMINDERS
from bot.exceptions import DoubleStore, ProblemToSaveInDB
from bot.settings_logs import logger
from bot.utils import Store
from database.connect import connect_to_db

load_dotenv()


async def create_to_db(store: Store):
    """Запись новых данных в БД"""
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
                INSERT INTO stores (sap_id, date_event, description)
                VALUES ($1, $2, $3)
                """,
                store.sap_id, store.date, store.description
            )
            logger.info(
                f"Магазин {store.sap_id} сохранен в БД "
                f"с евентом {store.description}"
            )
    except Exception as e:
        logger.error(f"Возникла ошибка при записи в БД: {e}")
        raise ProblemToSaveInDB(error=e)
    finally:
        await conn.close()


async def added_store_in_reminders_table(stores: list[Store]):
    """Добавление магазина в таблицу reminders"""
    conn = await connect_to_db()
    try:
        for store in stores:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO reminders (
                    store_id, status, last_notified_data
                    )
                    VALUES ($1, $2, $3)
                    """,
                    store.id, STATUSES_FOR_REMINDERS["cr"], datetime.now()
                )
            logger.info(f"Магазин {store.sap_id} добавлен в таблицу reminders")
    except Exception as e:
        logger.error(f"Возникла ошибка при записи в БД: {e}")
        raise ProblemToSaveInDB(error=e)
    finally:
        await conn.close()
