from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.constants import DESCRIPTION
from bot.exceptions import ProblemToGetUpdateDataWithDB
from bot.settings_logs import logger
from bot.utils import Store
from database.create import update_event_or_date_event


async def sap_id_for_change_description(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    """Получение sap_id"""
    logger.info("Запросили sap_id магазина")
    store: Store = context.user_data["store"]
    store.save_sap(update.message.text)

    reply_keyboard = [
        ["Открытие", "Закрытие"],
        ["Отключить задачи", "Включить задачи"]
    ]

    await update.message.reply_text(
        "Выбери событие или отправь /cancel для остановки",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=reply_keyboard, one_time_keyboard=True
        ),
    )

    return DESCRIPTION


async def description_for_change(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    logger.info("Получили sap магазина")
    store: Store = context.user_data["store"]
    store.description = update.message.text
    try:
        logger.info("Отправили данные для обновления")
        await update_event_or_date_event(
            sap_id=store.sap_id,
            description=store.description
        )
        logger.info("Данные обновлены")
        await update.message.reply_text(
            f"Событие для магазина {store.sap_id} обновлено"
        )
    except ProblemToGetUpdateDataWithDB as e:
        await update.message.reply_text(
            f"Возникла ошибка при обновлении данных: {e}"
        )
    finally:
        ConversationHandler.END
