from datetime import datetime

from bot.exceptions import (IncorrectDateOpenStore, IncorrectSapStore,
                            NotMessage)


class Store:
    """Класс для магазина"""

    def __init__(
            self,
            sap_id: int,
            date: datetime,
            description: str,
            id: int | None = None,
            chat_id: int | None = None,
            message_id: int | None = None
    ):
        self.id = id
        self.sap_id = sap_id
        self.date = date
        self.chat_id = chat_id
        self.description = description
        self.message_id = message_id

    @classmethod
    def convertation_from_message(cls, message: list, chat_id: int = None):
        """Метод класса для сохранения и преобразования даты в объект даты"""
        return cls(
            sap_id=message[0],
            date=datetime.strptime(message[1], "%d.%m.%Y").date(),
            description=message[2],
            chat_id=chat_id
        )

    @classmethod
    def convertation_from_db(cls, data: dict):
        return cls(
            id=data.get("id"),
            sap_id=data.get("sap_id"),
            date=data.get("date_event"),
            description=data.get("description"),
            chat_id=data.get("chat_id"),
            message_id=data.get("message_id", None)
        )


async def check_message(message: list) -> None:
    """Проверка полученного сообщения"""
    if len(message) < 2:
        raise NotMessage()
    elif len(message[0]) < 4:
        raise IncorrectSapStore()
    try:
        datetime.strptime(message[1], "%d.%m.%Y").date()
    except ValueError:
        raise IncorrectDateOpenStore()
