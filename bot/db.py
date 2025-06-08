import os

import asyncpg
from dotenv import load_dotenv
from datetime import datetime, timedelta
from exceptions import DoubleStore, ProblemConnectToDb, ProblemToJobWithDb, ProblemToSaveInDB
from utils import Store
from settings_logs import logger

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
        logger.info("Подключились к БД")
    except Exception as e:
        logger.error(f"Возникла ошибка при подключении к БД: {e}")
        raise ProblemConnectToDb(error=str(e))
    return conn


async def create_to_db(message: list, chat_id: int):
    """Запись новых данных в БД"""
    store = Store.preparation_for_db(message=message, chat_id=chat_id)
    conn = await connect_to_db()
    try:
        async with conn.transaction():
            double_data = await conn.fetch(
                "SELECT sap_id, date_event FROM stores WHERE sap_id = $1 and date_event = $2",
                store.sap_id, store.date
            )
            if double_data:
                raise DoubleStore()
            await conn.execute(
                "INSERT INTO stores (sap_id, date_event, chat_id) VALUES ($1, $2, $3, $4);",
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
                "SELECT * FROM stores WHERE date_event = $1",
                date
            )
        logger.info("Получили данные из БД")
    except Exception as e:
        logger.error(f"Возникла ошибка при получении магазинов из БД: {e}")
        raise ProblemToJobWithDb(str(e))
    finally:
        await conn.close()

    return values
