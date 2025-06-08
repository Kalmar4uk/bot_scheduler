from datetime import datetime, timedelta
from db import connect_to_db, get_stores
from exceptions import ErrorSendMessage
from settings_logs import logger
from telegram.ext import ApplicationBuilder


async def send_message(text: str, chat_id: int, app: ApplicationBuilder):
    """Отправка сообщения планировщика в чат"""
    try:
        await app.bot.send_message(chat_id=chat_id, text=text)
        logger.info("Отправили сообщение")
    except Exception as e:
        logger.error(
            f"Возникла ошибка при отправке сообщения планировщика: {e}"
        )
        raise ErrorSendMessage(e)


async def search_suitable_stores(app: ApplicationBuilder):
    """Поиск в БД подходящих объектов"""
    conn = await connect_to_db()
    logger.info("Подключились к БД")
    date: datetime = datetime.now().date() + timedelta(days=5)
    values = await get_stores()
    text: str = ""
    if values:
        chat_id: int = values[0]["chat_id"]
        for store in values:
            sap_id: str = store.get("sap_id")
            date: datetime = store.get("date_open")
            description: str = store.get("description")
            text += (
                f"Необходимо провести работы {description} "
                f"с СМ {sap_id} до {date}\n"
            )
        logger.info("Подготовили сообщение для отправки")
        await send_message(text=text, chat_id=chat_id, app=app)
    await conn.close()
