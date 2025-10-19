from .turnclass import TurnClass


class DayOpeningClass:

    def __init__(self, config_text: list):
        self._import(config_text)

    def _import(self, config_text: list):
        self._turns = []
        for turn in config_text:
            self._turns.append(TurnClass(config_text=turn))

    def closed(self):
        if len(self._turns) == 0:
            return True
        else:
            for turn in self._turns:
                if turn.closed():
                    return True
            return False

    def count(self):
        return len(self._turns)

    def turn(self, index: int):
        if 0 <= index < len(self._turns):
            return self._turns[index]
        else:
            raise ValueError("Turn index must be between 0 and " + str(len(self._turns) - 1))

    def to_string(self, separator: str = " | "):
        out = ""
        for index, turn in enumerate(self._turns):
            out += turn.to_string()
            if index < len(self._turns) - 1:
                out += separator

        return out

    def __str__(self):
        return self.to_string()