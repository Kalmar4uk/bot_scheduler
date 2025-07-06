from datetime import datetime


class Store:
    """Класс для магазина"""

    def __init__(
            self,
            sap_id: int | None = None,
            date: datetime | None = None,
            description: str | None = None,
            id: int | None = None,
    ):
        self.id = id
        self.sap_id = sap_id
        self.date = date
        self.description = description

    @classmethod
    def convertation_from_db(cls, data: dict):
        return cls(
            id=data.get("id"),
            sap_id=data.get("sap_id"),
            date=data.get("date_event"),
            description=data.get("description"),
        )

    def save_sap(self, sap: str):
        if sap.isalpha():
            new_sap = "B" + sap[1:]
            self.sap_id = new_sap
        else:
            self.sap_id = sap
