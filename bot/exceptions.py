class NotMessage(Exception):
    """Исключение в отсутствии данных в сообщении"""

    def __init__(self, error="Не соблюден шаблон или не переданы данные"):
        self.error = error
        super().__init__(self.error)


class IncorrectSapStore(Exception):
    """Исключение если Sap код состоит менее чем из 4х символов"""

    def __init__(self, error="Некорректный sap_id"):
        self.error = error
        super().__init__(self.error)


class IncorrectDateOpenStore(Exception):
    """Исключение если введено некорректное значение даты"""

    def __init__(self, error="Дата должна быть в формате ДД.ММ.ГГГГ"):
        self.error = error
        super().__init__(self.error)


class ProblemConnectToDb(Exception):
    """Исключение во время ошибки при подключении к БД"""

    def __init__(self, error=None):
        self.error = error
        super().__init__(self.error)


class ProblemToSaveInDB(Exception):
    """Ошибка при сохранении в БД"""

    def __init__(self, error=None):
        self.error = error
        super().__init__(self.error)


class ProblemToGetDataWithDB(Exception):
    """Ошибка при получении/обновлении данных в БД"""
    pass


class IncorrectChat(Exception):
    """Исключение попытки сохранения в личных сообщениях"""
    pass


class DoubleStore(Exception):
    """Исключение повторно добавления магазина"""

    def __init__(
            self,
            error="Данный магазин с такой датой события уже добавлен"
    ):
        self.error = error
        super().__init__(self.error)


class ErrorSendMessage(Exception):
    """Исключение ошибки отправления сообщения планировщика"""
    pass


class ErrorStartSchedule(Exception):
    """Исключение ошибки старта планировщика"""
    pass


class InvalidMessageId(Exception):
    """Исключение отсутствия или несоответствия message_id"""
    pass
