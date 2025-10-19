class TurnClass:

    def __init__(self, config_text: str):
        self._closed = False
        self.begins = None
        self.ends = None
        if config_text.strip().lower() == "closed":
            self._closed = True
        else:
            self._import(config_text)

    def _import(self, config_text: str):
        hypens = config_text.count("-")
        if hypens == 1:
            self.begins, self.ends = config_text.split("-")
            self.begins = self._clean_times(self.begins)
            self.ends = self._clean_times(self.ends)

    @staticmethod
    def _clean_times(time: str) -> str:
        colons = time.count(":")
        if colons == 1:
            hour, minute = time.split(":")
            if int(hour) < 0 or int(hour) > 23:
                raise ValueError("Hour must be between 0 and 23")
            elif int(minute) < 0 or int(minute) > 59:
                raise ValueError("Minute must be between 0 and 59")
            return time
        if colons == 0:
            if int(time) < 0 or int(time) > 23:
                raise ValueError("Hour must be between 0 and 23")
            return f"{time}:00"

        return time

    def closed(self) -> bool:
        return self._closed

    def to_string(self, separator: str = " - "):
        if self._closed:
            return "CLOSED"
        else:
            return f"{self.begins}{separator}{self.ends}"

    def __str__(self):
        return self.to_string()