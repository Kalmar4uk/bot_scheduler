import json

from telegram import (InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler
from telegram_bot_calendar import DetailedTelegramCalendar

from bot.constants import DESCRIPTION
from bot.exceptions import ProblemToSaveInDB
from bot.settings_logs import logger
from bot.utils import Store
from database.create import create_to_db
from bot.exceptions import ErrorSendMessage


async def sap_id_for_added_store(update: Update, context: CallbackContext):
    """Получение sap_id и активация инлайн календаря для ввода даты"""
    logger.info("Получили sap id магазина")
    store: Store = context.user_data["store"]
    store.save_sap(update.message.text)

    calendar_json, _ = DetailedTelegramCalendar(locale="ru").build()
    calendar_data = json.loads(calendar_json)

    reply_markup = InlineKeyboardMarkup(calendar_data["inline_keyboard"])

    try:
        await update.message.reply_text(
            "Выбери дату или отправь /cancel для остановки:",
            reply_markup=reply_markup
        )
        logger.info("Отправили календарь")
    except Exception as e:
        logger.error(f"Возникла ошибка при отправке календаря: {e}")
        raise ErrorSendMessage(e)


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

        try:
            await update.callback_query.edit_message_text(
                "Выбери дату или отправь /cancel для остановки:",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Возникла ошибка при отправке календаря: {e}")
            raise ErrorSendMessage(e)

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

        try:
            await update.callback_query.message.reply_text(
                "Выбери событие или отправь /cancel для остановки",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True
                ),
            )
            logger.info("Отправили сообщение с клавиатурой для евента")
        except Exception as e:
            logger.error(f"Возникла ошибка при отправке сообщения: {e}")
            raise ErrorSendMessage(e)

        return DESCRIPTION


async def description_for_added_store(
        update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Получение описания и сохранение магазина в БД"""
    store: Store = context.user_data["store"]
    store.description = update.message.text
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
