import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ERROR_SAVE_TO_DB: str = "Возникла ошибка при сохранении в БД"


STATUSES_FOR_REMINDERS = {
    "cr": "created",
    "rp": "repeat",
    "cn": "confirm",
    "ex": "expired"

}

SAP = 0
DESCRIPTION = 1
DATE = 1
EVENT = 1
