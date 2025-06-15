import os

import nest_asyncio
import sentry_sdk
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters)

from bot.bot_handlers.handlers import (handlers_added_store,
                                       handlers_change_date_event,
                                       start_handler)
from bot.constants import TOKEN
from bot.exceptions import ErrorStartSchedule
from bot.scheduler_handlers import (search_messages_without_response,
                                    search_suitable_stores)
from bot.settings_logs import logger
from database.db import messages_to_expired

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
            CronTrigger(hour=9, minute=30),
            id="daily_check",
            timezone="Europe/Moscow",
            kwargs={"app": app}
        )
        scheduler.add_job(
            search_messages_without_response,
            CronTrigger(hour=9, minute=20),
            id="repeat_check",
            timezone="Europe/Moscow",
            kwargs={"app": app}
        )
        scheduler.add_job(
            messages_to_expired,
            CronTrigger(hour=7),
            id="expired",
            timezone="Europe/Moscow"
        )
        scheduler.start()
        logger.info("Запустили планировщик")
    except Exception as e:
        logger.error(e)
        raise ErrorStartSchedule(
            f"Возникла ошибка при запуске планировщика: {e}"
        )
    return scheduler


async def setup() -> None:
    """Главная функция запусков"""
    await setup_scheduler()
    await start_handler(app=app)
    await handlers_added_store(app=app)
    await handlers_change_date_event(app=app)

    try:
        await app.run_polling()
    except (KeyboardInterrupt, RuntimeError):
        logger.info("Принудительная остановка бота")
