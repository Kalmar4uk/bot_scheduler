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


class ProblemToGetUpdateDataWithDB(Exception):
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


class NotReplyId(Exception):
    """Исключение при отсутсвии у сообщения reply_id"""
    def __init__(self, error="Сообщение не является ответом на напоминание"):
        self.error = error
        super().__init__(self.error)


class ReplyIsEmpty(Exception):
    """Исключение при отсутствии полученного message_id в базе"""
    def __init__(
            self,
            error="message_id отсутствует в базе",
            message_id: int = None
    ):
        self.error = error
        self.message_id = message_id
        super().__init__(self.error, message_id)
