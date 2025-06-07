import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
TEMPLATE: str = (
    "Шаблон который ожидает получить бот:\n"
    "B111 01.01.2020"
)
ERROR_SAVE_TO_IN_PRIVATE: str = "Сохранение возможно только в групповом чате"
ERROR_SAVE_TO_DB: str = "Возникла ошибка при сохранении в БД"
