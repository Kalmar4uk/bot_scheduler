from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ConversationHandler, MessageHandler, filters)

from bot.bot_handlers.added_store import (calendar_for_added_store,
                                          description_for_added_store,
                                          sap_id_for_added_store)
from bot.bot_handlers.change_date_event import (calendar_for_change_date,
                                                sap_id_for_change_date)
from bot.bot_handlers.change_event import (sap_id_for_change_description,
                                           description_for_change)
from bot.bot_handlers.default import (add_store, cancel, change_date,
                                      change_event, start)
from bot.constants import DESCRIPTION, SAP


async def start_handler(app: Application):
    app.add_handler(CommandHandler("start", start))


async def handlers_added_store(app: Application) -> None:

    added_store = ConversationHandler(
        entry_points=[
            CommandHandler("add_store", add_store)
        ],
        states={
            SAP: [
                MessageHandler(
                    filters.Regex("^(\\d{4}|[BbВ]\\d{3})$"),
                    sap_id_for_added_store
                ),
                CallbackQueryHandler(calendar_for_added_store)
            ],
            DESCRIPTION: [
                MessageHandler(
                    filters.Regex(
                        "^(Открытие|Закрытие|Отключить задачи|Включить задачи)$"
                    ),
                    description_for_added_store
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(added_store)


async def handlers_change_date_event(app: Application):

    change_date_event = ConversationHandler(
        entry_points=[
            CommandHandler("change_date", change_date)
        ],
        states={
            SAP: [
                MessageHandler(
                    filters.Regex("^(\\d{4}|[BbВ]\\d{3})$"),
                    sap_id_for_change_date
                ),
                CallbackQueryHandler(calendar_for_change_date)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(change_date_event)


async def handlers_change_event(app: Application):

    change_description_event = ConversationHandler(
        entry_points=[
            CommandHandler("change_event", change_event)
        ],
        states={
            SAP: [
                MessageHandler(
                    filters.Regex("^(\\d{4}|[BbВ]\\d{3})$"),
                    sap_id_for_change_description
                )
            ],
            DESCRIPTION: [
                MessageHandler(
                    filters.Regex(
                        "^(Открытие|Закрытие|Отключить задачи|Включить задачи)$"
                    ),
                    description_for_change
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(change_description_event)
