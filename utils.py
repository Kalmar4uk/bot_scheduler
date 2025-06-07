import re
from datetime import datetime

from exceptions import IncorrectDateOpenStore, IncorrectSapStore, NotMessage


class Store:
    """Класс для магазина"""

    def __init__(
            self, sap_id: int,
            date: datetime,
            chat_id: int | None = None
    ):
        self.sap_id = sap_id
        self.date = date
        self.chat_id = chat_id

    @classmethod
    def preparation_for_db(cls, message: list, chat_id: int = None):
        """Метод класса для сохранения и преобразования даты в объект даты"""
        return cls(
            sap_id=message[0],
            date=datetime.strptime(message[1], "%d.%m.%Y").date(),
            chat_id=chat_id
        )


async def check_message(message: list):
    """Проверка полученно сообщения"""
    if len(message) < 2:
        raise NotMessage()
    elif len(message[0]) < 4:
        raise IncorrectSapStore()
    try:
        datetime.strptime(message[1], "%d.%m.%Y").date()
    except ValueError:
        raise IncorrectDateOpenStore()
