import json

from telegram import (InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import (Application, CallbackContext, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)
from telegram_bot_calendar import DetailedTelegramCalendar

from bot.constants import TOKEN
from test_write import Store

STEP = {"y": "год", "m": "месяц", "d": "день"}

SAP, DATE, DESCRIPTION = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["/add_store"], ["/change_date"], ["/change_event"]]

    context.user_data["store"] = Store()

    await update.message.reply_text(
        "Необходимо выбрать, что нужно сделать или отправь /cancel для остановки",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )


async def add_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введи sap магазина или отправь /cancel для остановки"
    )
    return SAP


async def sap_id(update: Update, context: CallbackContext):
    store_sap: Store = context.user_data["store"]
    store_sap.save_sap(update.message.text)
    calendar_json, step = DetailedTelegramCalendar(locale="ru").build()
    calendar_data = json.loads(calendar_json)
    reply_markup = InlineKeyboardMarkup(calendar_data["inline_keyboard"])
    await update.message.reply_text("Выбери дату или отправь /cancel для остановки:", reply_markup=reply_markup)
    return DESCRIPTION


async def calendar(update: Update, context: CallbackContext):
    result, key, step = DetailedTelegramCalendar(
        locale="ru"
    ).process(
        update.callback_query.data
    )

    if not result and key:
        key = json.loads(key)
        reply_markup = InlineKeyboardMarkup(key["inline_keyboard"])

        await update.callback_query.edit_message_text(
            "Выбери дату или отправь /cancel для остановки:",
            reply_markup=reply_markup
        )
    elif result:
        await update.callback_query.edit_message_text(
            f"Выбрана дата: {result}"
        )
        store_date: Store = context.user_data["store"]
        store_date.date = result

        reply_keyboard = [
            ["Открытие", "Закрытие"],
            ["Отключить задачи", "Включить задачи"]
        ]

        await update.callback_query.message.reply_text(
            "Выбери событие или отправь /cancel для остановки",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True
            ),
        )


async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store_description: Store = context.user_data["store"]
    store_description.description = update.message.text
    print(store_description.description)
    await update.message.reply_text(
        "Записал",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Запись остановлена",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    added_store = ConversationHandler(
        entry_points=[
            CommandHandler("add_store", add_store),
            CommandHandler("cancel", cancel)
        ],
        states={
            SAP: [
                MessageHandler(filters.Regex("^(\\d{4}|[Bb]\\d{3})$"), sap_id),
                CommandHandler("cancel", cancel)
            ],
            DESCRIPTION: [
                MessageHandler(
                    filters.Regex(
                        "^(Открытие|Закрытие|Отключить задачи|Включить задачи)$"
                    ),
                    description
                ),
                CommandHandler("cancel", cancel)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(added_store)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(calendar))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
