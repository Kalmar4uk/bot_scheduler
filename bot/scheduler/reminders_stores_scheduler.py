from telegram.ext import ApplicationBuilder

from bot.scheduler.messages import send_message
from bot.settings_logs import logger
from bot.utils import Store
from database.get import get_reminders_for_repeat
from database.update import update_reminders_for_repeat


async def search_messages_without_response(app: ApplicationBuilder) -> None:
    """Поиск в БД сообщений на которые не было реакции"""
    logger.info("Начинаем поиск магазинов для отправки повторного напоминания")
    values = await get_reminders_for_repeat()
    text: str = (
        "Повторное оповещение для магазинов "
        "на которые не получено подтверждение:\n"
    )
    if values:
        stores: list[Store] = []
        for data in values:
            store = Store.convertation_from_db(data=data)
            text += (
                f"Магазин {store.sap_id} дата {store.date}, "
                f"выполнить {store.description}\n"
            )
            stores.append(store)
        logger.info("Подготовили сообщение для отправки")
        await send_message(text=text, app=app, stores=stores)
        logger.info(
            "Отправили данные для обновления статуса в таблице reminders"
        )
        await update_reminders_for_repeat(
            stores=stores
        )
        logger.info("Данные обновлены")
    else:
        logger.info("Нет подходящих магазинов для повторения")
