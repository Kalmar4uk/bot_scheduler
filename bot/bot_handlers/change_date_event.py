import json

from telegram import InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler
from telegram_bot_calendar import DetailedTelegramCalendar

from bot.exceptions import ProblemToGetUpdateDataWithDB
from bot.settings_logs import logger
from bot.utils import Store
from database.db import update_event_or_date_event


async def sap_id_for_change_date(update: Update, context: CallbackContext):
    """Получение sap_id и активация инлайн календаря для ввода даты"""
    logger.info("Запросили sap_id магазина")
    store: Store = context.user_data["store"]
    store.save_sap(update.message.text)

    calendar_json, _ = DetailedTelegramCalendar(locale="ru").build()
    calendar_data = json.loads(calendar_json)

    reply_markup = InlineKeyboardMarkup(calendar_data["inline_keyboard"])

    await update.message.reply_text(
        "Выбери дату или отправь /cancel для остановки:",
        reply_markup=reply_markup
    )


async def calendar_for_change_date(update: Update, context: CallbackContext):
    """Работа с календарем"""
    result, key, _ = DetailedTelegramCalendar(
        locale="ru"
    ).process(
        update.callback_query.data
    )

    if not result and key:
        key = json.loads(key)
        reply_markup = InlineKeyboardMarkup(key["inline_keyboard"])

        await update.callback_query.edit_message_text(
            "Выбери новую дату или отправь /cancel для остановки:",
            reply_markup=reply_markup
        )
    elif result:
        await update.callback_query.edit_message_text(
            f"Выбрана дата: {result}"
        )
        store: Store = context.user_data["store"]
        store.date = result
        logger.info("Отправили данные для обновления")
        try:
            await update_event_or_date_event(
                sap_id=store.sap_id,
                date=store.date
            )
            logger.info("Данные обновлены")
            await update.callback_query.message.reply_text(
                f"Дата события для магазина {store.sap_id} обновлена"
            )
        except ProblemToGetUpdateDataWithDB as e:
            await update.callback_query.message.reply_text(
                f"Возникла ошибка при обновлении данных: {e}"
            )
        finally:
            return ConversationHandler.END


async def cancel_change_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Остановка диалога"""
    await update.message.reply_text(
        "Запись остановлена",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
