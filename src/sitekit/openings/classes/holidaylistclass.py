from .holidayclass import HolidayClass


class HolidayListClass:

    def __init__(self):
        self._list = []

    def append(self, label: str, data: list):
        new_holiday = HolidayClass(label=label, data=data)
        self._list.append(new_holiday)