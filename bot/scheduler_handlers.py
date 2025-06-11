from datetime import datetime, timedelta

from telegram import Message
from telegram.ext import ApplicationBuilder

from database.db import added_store_in_reminders_table, connect_to_db, get_stores
from bot.exceptions import (ErrorSendMessage, InvalidMessageId,
                            ProblemToGetUpdateDataWithDB)
from bot.settings_logs import logger
from bot.utils import Store


async def send_message(
        text: str, chat_id: int, app: ApplicationBuilder
) -> int:
    """Отправка сообщения планировщика в чат"""
    try:
        msg: Message = await app.bot.send_message(chat_id=chat_id, text=text)
        logger.info("Отправили сообщение")
    except Exception as e:
        logger.error(
            f"Возникла ошибка при отправке сообщения планировщика: {e}"
        )
        raise ErrorSendMessage(e)
    return msg.message_id


async def search_suitable_stores(app: ApplicationBuilder) -> None:
    """Поиск в БД подходящих объектов"""
    conn = await connect_to_db()
    try:
        values = await get_stores()
    except ProblemToGetUpdateDataWithDB:
        await conn.close()
    text: str = ""
    stores_for_reminders: list[Store] = []
    if values:
        chat_id: int = values[0].get("chat_id")
        for data in values:
            store = Store.convertation_from_db(data=data)
            text += (
                f"Необходимо провести работы {store.description} "
                f"с СМ {store.sap_id} до {store.date}\n"
            )
            stores_for_reminders.append(store)
        logger.info("Подготовили сообщение для отправки")
        msg: int = await send_message(text=text, chat_id=chat_id, app=app)
        if not (msg and isinstance(msg, int)):
            logger.error("message_id не поступил или его тип не соответствует")
            raise InvalidMessageId()
        logger.info("Отправили данные для добавления в таблицу reminders")
        await added_store_in_reminders_table(
            stores=stores_for_reminders,
            message_id=msg
        )
    else:
        logger.info("Нет новых подходящих магазинов")
    await conn.close()
