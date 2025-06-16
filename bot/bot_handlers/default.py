from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.constants import SAP
from bot.exceptions import ErrorSendMessage
from bot.settings_logs import logger
from bot.utils import Store


async def base_func_request_sat(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    """Базовая функция запроса сап номера"""
    await update.message.reply_text(
        "Введи sap магазина или отправь /cancel для остановки"
    )
    return SAP


async def add_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Первая функция в начале диалога добавления магазина"""
    context.user_data["store"] = Store()

    return await base_func_request_sat(update=update, context=context)


async def change_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Первая функция в начале диалога обновления даты события"""
    context.user_data["store"] = Store()

    return await base_func_request_sat(update=update, context=context)


async def change_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Первая функция в начале диалога обновления события"""
    context.user_data["store"] = Store()

    return await base_func_request_sat(update=update, context=context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Остановка диалога"""
    await update.message.reply_text(
        "Запись остановлена",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Описание команд"""
    reply_keyboard = [["/add_store"], ["/change_date"], ["/change_event"]]

    output = (
        f"Привет {update.message.from_user.username}.\n"
        f"Выбери необходимое действие:\n"
        f"/add_store - Добавление нового магазина в напоминание\n"
        f"/change_date - Изменение даты события для магазина\n"
        f"/change_event - Изменение события для магазина"
    )
    try:
        await update.message.reply_text(
            text=output,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=reply_keyboard,
                one_time_keyboard=True)
        )
    except Exception as e:
        logger.error(
            f"Возникла ошибка при отправке сообщения: {e}"
        )
        raise ErrorSendMessage(e)
