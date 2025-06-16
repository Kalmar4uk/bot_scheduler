import os

import asyncpg
from dotenv import load_dotenv

from bot.exceptions import ProblemConnectToDb
from bot.settings_logs import logger

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
