from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Message,
                      Update)
from telegram.ext import ApplicationBuilder, CallbackContext

from bot.constants import CHAT_ID
from bot.exceptions import ErrorSendMessage, ProblemToGetUpdateDataWithDB
from bot.settings_logs import logger
from bot.utils import Store
from database.update import update_store_received_confirmation


async def send_message(
        text: str,
        app: ApplicationBuilder,
        stores: list[Store]
) -> int:
    """Отправка сообщения планировщика в чат"""
    if len(stores) > 1:
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"Под-ть {store.sap_id}",
                    callback_data=store.sap_id
                ) for store in stores
            ],
            [
                InlineKeyboardButton(
                    text="Подтвердить все",
                    callback_data=",".join([store.sap_id for store in stores])
                )
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"Под-ть {stores[0].sap_id}",
                    callback_data=f"{stores[0].sap_id}"
                )
            ]
        ]
    reply = InlineKeyboardMarkup(keyboard)
    try:
        msg: Message = await app.bot.send_message(
            chat_id=CHAT_ID, text=text, reply_markup=reply
        )
        logger.info(f"Отправили сообщение {msg.text}")
    except Exception as e:
        logger.error(
            f"Возникла ошибка при отправке сообщения планировщика: {e}"
        )
        raise ErrorSendMessage(e)


async def confirm_button(update: Update, context: CallbackContext):
    """Получение ответа с кнопки уведомления"""
    logger.info("Получили ответ с кнопки")
    query = update.callback_query
    keyboard = query.message.reply_markup.inline_keyboard
    query_data = query.data

    await query.answer()

    if len(query_data) > 4:
        logger.info("Получили более одного магазина")
        list_query_data = query_data.split(",")

        try:
            logger.info("Отправили данные для перевода статуса магазинов")
            await update_store_received_confirmation(store=list_query_data)
        except ProblemToGetUpdateDataWithDB:
            await query.message.reply_text(
                "Возникла ошибка при обновлении магазинов, попробуй еще раз"
            )
            raise

        await query.edit_message_text("Сохранил")

    else:
        logger.info("Получили магазин")
        try:
            logger.info("Отправили данные для перевода статуса магазина")
            await update_store_received_confirmation(store=query_data)
        except ProblemToGetUpdateDataWithDB:
            await query.message.reply_text(
                "Возникла ошибка при обновлении магазинов, попробуй еще раз"
            )
            raise

        if len(keyboard) > 1:
            await query.message.reply_text(
                f"Сохранил магазин {query_data}, "
                f"если решил подтвердить другой, "
                f"выбери его или 'Подвердить все'"
            )
        else:
            await query.edit_message_text("Сохранил")

    logger.info("Отправили сообщение в чат")
