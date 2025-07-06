from telegram.ext import ApplicationBuilder

from bot.exceptions import ProblemToGetUpdateDataWithDB
from bot.scheduler.messages import send_message
from bot.settings_logs import logger
from bot.utils import Store
from database.create import added_store_in_reminders_table
from database.get import get_stores


async def search_suitable_stores(app: ApplicationBuilder) -> None:
    """Поиск в БД подходящих объектов"""
    logger.info("Начинаем поиск магазинов для отправки напоминания")
    try:
        values = await get_stores()
    except ProblemToGetUpdateDataWithDB:
        raise
    text: str = "Необходимо провести работы\n"
    stores: list[Store] = []
    if values:
        for data in values:
            store = Store.convertation_from_db(data=data)
            text += (
                f"С {store.sap_id} до {store.date}, "
                f"выполнить {store.description}\n"
            )
            stores.append(store)
        logger.info("Подготовили сообщение для отправки")
        await send_message(
            text=text,
            app=app,
            stores=stores
        )
        logger.info("Отправили данные для добавления в таблицу reminders")
        await added_store_in_reminders_table(stores=stores)
    else:
        logger.info("Нет новых подходящих магазинов")
