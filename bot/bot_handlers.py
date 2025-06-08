from constants import ERROR_SAVE_TO_DB, ERROR_SAVE_TO_IN_PRIVATE, TEMPLATE
from db import create_to_db
from exceptions import (ErrorSendMessage, IncorrectChat,
                        IncorrectDateOpenStore, IncorrectSapStore, NotMessage,
                        ProblemToSaveInDB)
from settings_logs import logger
from telegram import Update
from telegram.ext import ContextTypes
from utils import check_message


async def waiting_for_response(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    """Получение ответа на уведомление"""
    try:
        msg: int = update.message.reply_to_message.message_id
    except AttributeError:
        pass



async def new_store(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получение/проверка/запись сообщения"""
    chat = update.effective_chat
    if chat.type == "private":
        await context.bot.send_message(
            chat_id=chat.id,
            text=ERROR_SAVE_TO_IN_PRIVATE
        )
        raise IncorrectChat(ERROR_SAVE_TO_IN_PRIVATE)
    try:
        message = update.message.text.replace(
            "/new_store", ""
        ).strip().split(" ")
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat.id, text=f"error: {str(e)}"
        )
        logger.error("Возникла ошибка при преобразовании сообщения из чата")
    try:
        await check_message(message=message)
    except NotMessage as e:
        await context.bot.send_message(
            chat_id=chat.id, text=f"error: {str(e)}"
        )
    except IncorrectSapStore as e:
        await context.bot.send_message(
            chat_id=chat.id, text=f"error: {str(e)}"
        )
    except IncorrectDateOpenStore as e:
        await context.bot.send_message(
            chat_id=chat.id, text=f"error: {str(e)}"
        )
    else:
        try:
            logger.info("Отправили данные для сохранения в БД")
            await create_to_db(message=message, chat_id=chat.id)
            logger.info("Данные сохранены")
            await context.bot.send_message(chat_id=chat.id, text="Записал")
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"{ERROR_SAVE_TO_DB}: {e}"
            )
            raise ProblemToSaveInDB(error=e)


async def example_template(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    try:
        await context.bot.send_message(chat_id=chat.id, text=TEMPLATE)
    except Exception as e:
        logger.error(
            f"Возникла ошибка при отправке сообщения: {e}"
        )
        raise ErrorSendMessage(e)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие бота"""
    chat = update.effective_chat
    output = (
        f"Привет {update.message.from_user.username}.\n"
        f"Для добавления магазина используй команду /new_store "
        f"написанную по шаблону, для просмотра шаблона используй /template.\n"
    )
    try:
        await context.bot.send_message(chat_id=chat.id, text=output)
    except Exception as e:
        logger.error(
            f"Возникла ошибка при отправке сообщения: {e}"
        )
        raise ErrorSendMessage(e)
