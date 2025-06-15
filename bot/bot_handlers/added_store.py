import json

from telegram import (InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler
from telegram_bot_calendar import DetailedTelegramCalendar

from bot.constants import DESCRIPTION
from bot.exceptions import ProblemToSaveInDB
from bot.settings_logs import logger
from bot.utils import Store
from database.db import create_to_db


async def sap_id_for_added_store(update: Update, context: CallbackContext):
    """Получение sap_id и активация инлайн календаря для ввода даты"""
    store: Store = context.user_data["store"]
    store.save_sap(update.message.text)

    calendar_json, _ = DetailedTelegramCalendar(locale="ru").build()
    calendar_data = json.loads(calendar_json)

    reply_markup = InlineKeyboardMarkup(calendar_data["inline_keyboard"])

    await update.message.reply_text(
        "Выбери дату или отправь /cancel для остановки:",
        reply_markup=reply_markup
    )

    return DESCRIPTION


async def calendar_for_added_store(update: Update, context: CallbackContext):
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
            "Выбери дату или отправь /cancel для остановки:",
            reply_markup=reply_markup
        )
    elif result:
        logger.info("Получили данные из календаря")
        await update.callback_query.edit_message_text(
            f"Выбрана дата: {result}"
        )
        store: Store = context.user_data["store"]
        store.date = result

        reply_keyboard = [
            ["Открытие", "Закрытие"],
            ["Отключить задачи", "Включить задачи"]
        ]

        await update.callback_query.message.reply_text(
            "Выбери событие или отправь /cancel для остановки",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True
            ),
        )


async def description_for_added_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение описания и сохранение магазина в БД"""
    chat_id: int = update.effective_chat.id
    store: Store = context.user_data["store"]
    store.description = update.message.text
    store.chat_id = chat_id
    try:
        logger.info("Отправили данные для сохранения в БД")
        await create_to_db(store=store)
        logger.info("Сохранили новый магазин в БД")
        await update.message.reply_text(
            "Записал",
            reply_markup=ReplyKeyboardRemove()
        )
    except ProblemToSaveInDB as e:
        await update.message.reply_text(text=e)
    finally:
        return ConversationHandler.END


async def cancel_added_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Остановка диалога"""
    await update.message.reply_text(
        "Запись остановлена",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
