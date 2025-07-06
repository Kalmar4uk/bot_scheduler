from datetime import datetime, timedelta

from dotenv import load_dotenv

from bot.constants import STATUSES_FOR_REMINDERS
from bot.exceptions import ProblemToGetUpdateDataWithDB
from bot.settings_logs import logger
from database.connect import connect_to_db

load_dotenv()


async def get_stores():
    """Получение магазинов из БД"""
    conn = await connect_to_db()
    date: datetime = datetime.now().date() + timedelta(days=1)
    try:
        async with conn.transaction():
            values = await conn.fetch(
                """
                SELECT s.id, s.sap_id, s.date_event, s.description
                FROM stores s
                WHERE s.date_event = $1
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
                s.description
                FROM stores s
                JOIN reminders r ON r.store_id = s.id
                WHERE r.status not in ($1, $2) and r.created_at < $3
                """,
                STATUSES_FOR_REMINDERS["cn"],
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
