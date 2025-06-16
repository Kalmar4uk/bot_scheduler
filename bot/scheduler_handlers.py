from telegram import Message
from telegram.ext import ApplicationBuilder

from bot.constants import CHAT_ID
from bot.exceptions import (ErrorSendMessage, InvalidMessageId,
                            ProblemToGetUpdateDataWithDB)
from bot.settings_logs import logger
from bot.utils import Store
from database.create import added_store_in_reminders_table
from database.get import get_reminders_for_repeat, get_stores
from database.update import update_reminders_for_repeat


async def send_message(
        text: str, app: ApplicationBuilder
) -> int:
    """Отправка сообщения планировщика в чат"""
    try:
        msg: Message = await app.bot.send_message(chat_id=CHAT_ID, text=text)
        logger.info(f"Отправили сообщение {msg}")
    except Exception as e:
        logger.error(
            f"Возникла ошибка при отправке сообщения планировщика: {e}"
        )
        raise ErrorSendMessage(e)
    return msg.message_id


async def search_suitable_stores(app: ApplicationBuilder) -> None:
    """Поиск в БД подходящих объектов"""
    logger.info("Начинаем поиск магазинов для отправки напоминания")
    try:
        values = await get_stores()
    except ProblemToGetUpdateDataWithDB:
        raise
    text: str = ""
    stores_for_reminders: list[Store] = []
    if values:
        for data in values:
            store = Store.convertation_from_db(data=data)
            text += (
                f"Необходимо провести работы {store.description} "
                f"с СМ {store.sap_id} до {store.date}\n"
            )
            stores_for_reminders.append(store)
        logger.info("Подготовили сообщение для отправки")
        msg: int = await send_message(text=text, app=app)
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


async def search_messages_without_response(app: ApplicationBuilder) -> None:
    """Поиск в БД сообщений на которые не было реакции"""
    logger.info("Начинаем поиск магазинов для отправки повторного напоминания")
    values = await get_reminders_for_repeat()
    message_ids_for_reminders: list[int] = []
    text: str = (
        "Повторное оповещение для магазинов "
        "на которые не получено подтверждение:\n"
    )
    if values:
        for data in values:
            store = Store.convertation_from_db(data=data)
            text += f"Магазин {store.sap_id} дата {store.date}\n"
            message_ids_for_reminders.append(store.message_id)
        logger.info("Подготовили сообщение для отправки")
        await send_message(text=text, app=app)
        logger.info(
            "Отправили данные для обновления статуса в таблице reminders"
        )
        await update_reminders_for_repeat(
            message_ids=message_ids_for_reminders
        )
        logger.info("Данные обновлены")
    else:
        logger.info("Нет новых подходящих магазинов")
