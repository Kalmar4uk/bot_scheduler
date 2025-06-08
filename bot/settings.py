import asyncio
import os
import nest_asyncio
import sentry_sdk
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from constants import TOKEN
from exceptions import ErrorStartSchedule
from settings_logs import logger
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from scheduler_handlers import search_suitable_stores
from bot_handlers import hello, new_store, example_template, waiting_for_response

load_dotenv()
nest_asyncio.apply()

app = ApplicationBuilder().token(TOKEN).build()

sentry_sdk.init(os.getenv("DSN"))


async def setup_scheduler() -> AsyncIOScheduler:
    """Инициализация обработчика"""
    global app
    try:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            search_suitable_stores,
            CronTrigger(hour=17, minute=49),
            id="daily_check",
            timezone="Europe/Moscow",
            kwargs={"app": app}
        )
        scheduler.start()
        logger.info("Запустили планировщик")
    except Exception as e:
        logger.error(e)
        raise ErrorStartSchedule(
            f"Возникла ошибка при запуске планировщика: {e}"
        )
    return scheduler


async def main() -> None:
    """Главная функция запусков"""
    scheduler = await setup_scheduler()

    app.add_handler(CommandHandler("start", hello))
    app.add_handler(CommandHandler("template", example_template))
    app.add_handler(CommandHandler("new_store", new_store))
    app.add_handler(MessageHandler(filters.TEXT, waiting_for_response))

    try:
        await app.run_polling()
    except KeyboardInterrupt:
        logger.info("Принудительно завершили работу бота")
        print("Завершили работу")
    finally:
        await app.shutdown()
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
