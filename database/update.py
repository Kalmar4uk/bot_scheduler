from datetime import datetime

from dotenv import load_dotenv

from bot.constants import STATUSES_FOR_REMINDERS
from bot.exceptions import (ProblemToGetUpdateDataWithDB, ReplyIsEmpty,
                            StoreNotFound)
from bot.settings_logs import logger
from bot.utils import Store
from database.connect import connect_to_db

load_dotenv()


async def update_store_received_confirmation(
        store: list[str] | str
):
    """Обновление магазинов по которым получили подтверждение"""
    conn = await connect_to_db()
    try:
        async with conn.transaction():
            if isinstance(store, list):
                await conn.execute(
                    """
                    UPDATE reminders
                    SET status = $1, last_notified_data = $2
                    WHERE store_id in (
                    SELECT s.id FROM stores s WHERE s.sap_id = ANY($3::text[])
                    ) AND status not in ($4, $5)
                    """,
                    STATUSES_FOR_REMINDERS["cn"],
                    datetime.now(),
                    store,
                    STATUSES_FOR_REMINDERS["cn"],
                    STATUSES_FOR_REMINDERS["ex"]
                )
            else:
                await conn.execute(
                    """
                    UPDATE reminders
                    SET status = $1, last_notified_data = $2
                    WHERE store_id = (
                    SELECT s.id FROM stores s WHERE s.sap_id = $3
                    ) AND status not in ($4, $5)
                    """,
                    STATUSES_FOR_REMINDERS["cn"],
                    datetime.now(),
                    store,
                    STATUSES_FOR_REMINDERS["cn"],
                    STATUSES_FOR_REMINDERS["ex"]
                )
    except Exception as e:
        logger.error(f"Возникла ошибка при обновлении магазинов: {e}")
        raise ProblemToGetUpdateDataWithDB(str(e))
    finally:
        await conn.close()


async def update_reminders_for_repeat(stores: list[Store]):
    """Обновление статуса повторного напоминания"""
    conn = await connect_to_db()
    stores_id = [store.id for store in stores]
    try:
        async with conn.transaction():
            await conn.execute(
                """
                UPDATE reminders
                SET status = $1, last_notified_data = $2
                WHERE store_id = ANY($3)
                AND status not in ($4, $5)
                AND created_at < $2
                """,
                STATUSES_FOR_REMINDERS["rp"],
                datetime.now(),
                (stores_id,),
                STATUSES_FOR_REMINDERS["cn"],
                STATUSES_FOR_REMINDERS["ex"]
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


async def update_event_or_date_event(
        sap_id: str,
        date: datetime | None = None,
        description: str | None = None
):
    """Обновление даты или события магазина"""
    conn = await connect_to_db()
    try:
        async with conn.transaction():
            if date:
                values = await conn.execute(
                    """
                    UPDATE stores
                    SET date_event = $1
                    WHERE sap_id = $2 and date_event > $3
                    """,
                    date, sap_id, datetime.now()
                )
            elif description:
                values = await conn.execute(
                    """
                    UPDATE stores
                    SET description = $1
                    WHERE sap_id = $2 and date_event > $3
                    """,
                    description, sap_id, datetime.now()
                )
        if int(values[-1]) == 0:
            raise StoreNotFound()
    except Exception as e:
        logger.error(f"Возникла ошибка при обновлении магазинов: {e}")
        raise ProblemToGetUpdateDataWithDB(str(e))
    finally:
        await conn.close()
