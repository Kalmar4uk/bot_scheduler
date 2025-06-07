import os

import asyncpg
from dotenv import load_dotenv
from exceptions import ProblemConnectToDb, DoubleStore
from utils import Store

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
        raise ProblemConnectToDb(error=str(e))
    return conn


async def create_to_db(message: list, chat_id: int):
    """Запись новых данных в БД"""
    store = Store.preparation_for_db(message=message, chat_id=chat_id)
    conn = await connect_to_db()
    try:
        async with conn.transaction():
            double_data = await conn.fetch(
                "SELECT sap_id, date_open FROM stores WHERE sap_id = $1 and date_open = $2",
                store.sap_id, store.date
            )
            if double_data:
                raise DoubleStore()
            await conn.execute(
                "INSERT INTO stores (sap_id, date_open, chat_id) VALUES ($1, $2, $3);",
                store.sap_id, store.date, store.chat_id
            )
    finally:
        await conn.close()
