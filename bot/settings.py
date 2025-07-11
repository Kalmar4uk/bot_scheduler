import os

import nest_asyncio
import sentry_sdk
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CallbackQueryHandler

from bot.bot_handlers.handlers import (handlers_added_store,
                                       handlers_change_date_event,
                                       handlers_change_event, start_handler)
from bot.constants import TOKEN
from bot.exceptions import ErrorStartSchedule
from bot.scheduler.messages import confirm_button
from bot.scheduler.new_stores_scheduler import search_suitable_stores
from bot.scheduler.reminders_stores_scheduler import \
    search_messages_without_response
from bot.settings_logs import logger
from database.update import messages_to_expired

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
            CronTrigger(hour=14, minute=35, second=10),
            id="daily_check",
            timezone="Europe/Moscow",
            kwargs={"app": app}
        )
        scheduler.add_job(
            search_messages_without_response,
            CronTrigger(hour=14, minute=10, second=40),
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
    await handlers_change_event(app=app)
    await handlers_change_date_event(app=app)
    app.add_handler(CallbackQueryHandler(confirm_button))

    try:
        await app.run_polling()
    except (KeyboardInterrupt, RuntimeError):
        logger.info("Принудительная остановка бота")
