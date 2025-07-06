import json
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Message,
                      Update)
from telegram.ext import ApplicationBuilder, CallbackContext

from bot.constants import CHAT_ID
from bot.exceptions import ErrorSendMessage, ProblemToGetUpdateDataWithDB
from bot.settings_logs import logger
from bot.utils import Store
from database.get import get_stores
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
                    text=f"Под-ть {store}",
                    callback_data=f"confirm {store}"
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
    query_data = query.data

    await query.answer()

    if len(query_data) > 4:
        logger.info("Получили более одного магазина")
        try:
            stores_data = await get_stores()
            logger.info("Получили магазины")
        except ProblemToGetUpdateDataWithDB:
            await query.message.reply_text(
                "Возникла ошибка при получении магазинов, попробуй еще раз"
            )
            raise

        stores = [
            Store.convertation_from_db(data=store).sap_id
            for store in stores_data
        ]

        try:
            logger.info("Отправили данные для перевода статуса магазинов")
            await update_store_received_confirmation(store=stores)
        except ProblemToGetUpdateDataWithDB:
            await query.message.reply_text(
                "Возникла ошибка при обновлении магазинов, попробуй еще раз"
            )
            raise

        await query.edit_message_text("Сохранил")
        logger.info("Отправили сообщение в чат")

    else:
        logger.info("Получили один магазин")
        change_store = query_data

        try:
            await update_store_received_confirmation(store=change_store)
        except ProblemToGetUpdateDataWithDB:
            await query.message.reply_text(
                "Возникла ошибка при обновлении магазина, попробуй еще раз"
            )
            raise

        await query.message.reply_text(
            f"Сохранил магазин {change_store}, "
            f"если решил подтвердить другой, "
            f"выбери его или 'Подвердить все'"
        )
        logger.info("Отправили сообщение в чат")
