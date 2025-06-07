import asyncio
from datetime import datetime, timedelta

import nest_asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from constants import (ERROR_SAVE_TO_DB, ERROR_SAVE_TO_IN_PRIVATE, TEMPLATE,
                       TOKEN)
from db import connect_to_db, create_to_db
from exceptions import (IncorrectChat, IncorrectDateOpenStore,
                        IncorrectSapStore, NotMessage, ProblemToSaveInDB)
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from utils import check_message

nest_asyncio.apply()

app = ApplicationBuilder().token(TOKEN).build()


async def send_message(text: str, chat_id: int):
    """Отправка сообщения планировщика в чат"""
    await app.bot.send_message(chat_id=chat_id, text=text)


async def search_suitable_stores():
    """Функция планировщика, поиск в БД подходящих объектов"""
    conn = await connect_to_db()
    date: datetime = datetime.now().date() + timedelta(days=5)
    values = await conn.fetch(
        "SELECT * FROM stores WHERE date_open = $1",
        date
    )
    text: str = ""
    if values:
        chat_id: int = values[0]["chat_id"]
        for store in values:
            sap_id: str = store["sap_id"]
            date: datetime = store["date_open"]
            text += f"Магазин {sap_id} открывается {date} пора его включить\n"
        await send_message(text=text, chat_id=chat_id)
    await conn.close()


async def new_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await create_to_db(message=message, chat_id=chat.id)
            await context.bot.send_message(chat_id=chat.id, text="Записал")
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"{ERROR_SAVE_TO_DB}: {e}"
            )
            raise ProblemToSaveInDB(error=e)


async def example_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await context.bot.send_message(chat_id=chat.id, text=TEMPLATE)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие бота"""
    chat = update.effective_chat
    output = (
        f"Привет {update.message.from_user.username}.\n"
        f"Для добавления магазина используй команду /new_store "
        f"написанную по шаблону, для просмотра шаблона используй /template.\n"
        f"В дальнейшем добавлю выгрузку в excel, но есть проблема с передачей файлов "
        f"телеграмме. По этому скорее всего просто дам доступ к БД."
        f"Добавление из личных сообщений невозможно!"
    )
    await context.bot.send_message(chat_id=chat.id, text=output)


async def setup_scheduler():
    """Инициализация обработчика"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        search_suitable_stores,
        CronTrigger(hour=10),
        id="daily_check",
        timezone="Europe/Moscow"
    )
    scheduler.start()
    return scheduler


async def main():
    """Главная функция запусков"""
    scheduler = await setup_scheduler()

    app.add_handler(CommandHandler("start", hello))
    app.add_handler(CommandHandler("template", example_template))
    app.add_handler(CommandHandler("new_store", new_store))

    try:
        await app.run_polling()
    finally:
        await app.shutdown()
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
