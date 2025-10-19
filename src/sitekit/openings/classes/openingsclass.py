from datetime import date, timedelta
from .dayopeningclass import DayOpeningClass
from .holidaylistclass import HolidayListClass


class OpeningsClass:

    def __init__(self, config_text: dict):
        self._import(config_text)

    def _import(self, config_text: dict):
        self._weekdays = []
        self._holidays = HolidayListClass()
        # Legge i giorni della settimana da lunedì (0) a domenica (6)
        for i in range(7):
            self._weekdays.append(DayOpeningClass(config_text=["CLOSED"]))
        for index, weekday in enumerate(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
            if config_text.get(weekday):
                self._weekdays[index] = DayOpeningClass(config_text=config_text[weekday])

        # Legge le eventuali aperture speciali indicate
        # nella voce "holidays"
        if config_text.get("holidays"):
            for holiday in config_text["holidays"]:
                value = config_text["holidays"][holiday]
                self._holidays.append(label=holiday, data=value)
        pass

    def weekday(self, day: int) -> DayOpeningClass:
        if 0 <= day <= 6:
            return self._weekdays[day]
        else:
            raise ValueError("day must be between 0 and 6")

    def monday(self) -> DayOpeningClass:
        return self._weekdays[0]

    def tuesday(self) -> DayOpeningClass:
        return self._weekdays[1]

    def wednesday(self) -> DayOpeningClass:
        return self._weekdays[2]

    def thursday(self) -> DayOpeningClass:
        return self._weekdays[3]

    def friday(self) -> DayOpeningClass | None:
        return self._weekdays[4]

    def saturday(self) -> DayOpeningClass | None:
        return self._weekdays[5]

    def sunday(self) -> DayOpeningClass | None:
        return self._weekdays[6]

    def today(self):
        now = date.today()
        return self.get(now)

    def tomorrow(self):
        now = date.today()
        return self.get(now + timedelta(days=1))

    def get(self, _date: date) -> DayOpeningClass:
        # TODO. Al momento non tiene conto delle aperture speciali
        return self.weekday(_date.weekday())