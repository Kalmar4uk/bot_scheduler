from datetime import datetime


class Store:

    def __init__(self, store_sap: str | None = None, date: datetime | None = None, description: str | None = None):
        self.store_sap = store_sap
        self.date = date
        self.description = description

    def save_sap(self, sap: str):
        if sap.isalpha():
            self.store_sap = sap.capitalize()
        else:
            self.store_sap = sap
