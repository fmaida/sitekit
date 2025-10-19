from datetime import date
from .turnclass import TurnClass


class HolidayClass:

    def __init__(self, label: str, data: list):
        self._import(label, data)

    def _import(self, label: str, data: list):
        self._set_label_and_date(label)
        self._turns = []
        for turn in data:
            new_turn = TurnClass(config_text=turn)
            self._turns.append(new_turn)

    def _set_label_and_date(self, label: str):
        self._label = label
        self._offset = 0
        if "-" in label.lower():
            # Si torna indietro nel tempo
            self._label, self._offset = label.split("-")
            self._offset = -int(self._offset)
        elif "+" in label.lower():
            # Si va avanti nel tempo
            self._label, self._offset = label.split("+")
            self._offset = int(self._offset)

    def easter_gauss(year):
        a = year % 19
        b = year % 4
        c = year % 7
        k = year // 100
        p = (13 + 8 * k) // 25
        q = k // 4
        M = (15 - p + k - q) % 30
        N = (4 + k - q) % 7
        d = (19 * a + M) % 30
        e = (2 * b + 4 * c + 6 * d + N) % 7
        day = 22 + d + e

        if day <= 31:
            return date(year, 3, day)
        else:
            return date(year, 4, day - 31)

    def __str__(self):
        out = f"<Holiday: \"{self._label}\""
        if self._offset != 0:
            out += f" offset={self._offset}"
        out += ">"

        return out