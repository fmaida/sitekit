import pytest
import datetime
from sitekit import openings
from sitekit.openings.classes.dayopeningclass import DayOpeningClass


@pytest.fixture(autouse=True, scope="module")
def timetable():
    return openings.load("demo/openings-simple.yaml")

def test_caricamento_file(timetable):
    assert isinstance(timetable, openings.OpeningsClass)

def test_funzionamento_turni_giornalieri(timetable):
    for i in range(7):
        assert isinstance(timetable.weekday(i), DayOpeningClass)
    assert isinstance(timetable.monday(), DayOpeningClass)
    assert isinstance(timetable.tuesday(), DayOpeningClass)
    assert isinstance(timetable.wednesday(), DayOpeningClass)
    assert isinstance(timetable.thursday(), DayOpeningClass)
    assert isinstance(timetable.friday(), DayOpeningClass)
    assert isinstance(timetable.saturday(), DayOpeningClass)
    assert isinstance(timetable.sunday(), DayOpeningClass)

def test_funzionamento_turno_lunedi(timetable):
    day = timetable.monday()
    assert str(day) == "11:30 - 15:30 | 18:00 - 23:30"
    assert day.count() == 2
    assert day.turn(0).begins == "11:30"
    assert day.turn(0).ends == "15:30"
    assert day.turn(1).begins == "18:00"
    assert day.turn(1).ends == "23:30"

def test_funzionamento_turno_martedi(timetable):
    day = timetable.tuesday()
    assert str(day) == "11:00 - 15:00 | 18:30 - 23:00"
    assert day.count() == 2
    assert day.turn(0).begins == "11:00"
    assert day.turn(0).ends == "15:00"
    assert day.turn(1).begins == "18:30"
    assert day.turn(1).ends == "23:00"

def test_funzionamento_turno_mercoledi(timetable):
    day = timetable.wednesday()
    assert str(day) == "CLOSED"
    assert day.closed() is True

def test_funzionamento_turno_giovedi(timetable):
    day = timetable.thursday()
    assert str(day) == "18:30 - 23:00"
    assert day.count() == 1
    assert day.turn(0).begins == "18:30"
    assert day.turn(0).ends == "23:00"

def test_funzionamento_turno_venerdi(timetable):
    day = timetable.friday()
    assert str(day) == "11:30 - 15:30 | 18:00 - 23:00"
    assert day.count() == 2
    assert day.turn(0).begins == "11:30"
    assert day.turn(0).ends == "15:30"
    assert day.turn(1).begins == "18:00"
    assert day.turn(1).ends == "23:00"

def test_funzionamento_turno_sabato(timetable):
    day = timetable.saturday()
    assert str(day) == "11:30 - 15:30 | 18:30 - 02:00"
    assert day.count() == 2
    assert day.turn(0).begins == "11:30"
    assert day.turn(0).ends == "15:30"
    assert day.turn(1).begins == "18:30"
    assert day.turn(1).ends == "02:00"

def test_funzionamento_turno_domenica(timetable):
    day = timetable.sunday()
    assert str(day) == "12:00 - 16:00 | 18:30 - 23:00"
    assert day.count() == 2
    assert day.turn(0).begins == "12:00"
    assert day.turn(0).ends == "16:00"
    assert day.turn(1).begins == "18:30"
    assert day.turn(1).ends == "23:00"

def test_funzionamento_turno_primo_gennaio_2025(timetable):
    day = timetable.get(datetime.date(2025, 1, 1))
    assert str(day) == "CLOSED"
    assert day.closed() is True

def test_funzionamento_turno_primo_gennaio_2026(timetable):
    day = timetable.get(datetime.date(2026, 1, 1))
    assert str(day) == "18:30 - 23:00"
    assert day.count() == 1
    assert day.turn(0).begins == "18:30"
    assert day.turn(0).ends == "23:00"

def test_funzionamento_turno_ferragosto_2026(timetable):
    day = timetable.get(datetime.date(2026, 8, 15))
    assert str(day) == "11:30 - 15:30 | 18:30 - 02:00"
    assert day.count() == 2
    assert day.turn(0).begins == "11:30"
    assert day.turn(0).ends == "15:30"
    assert day.turn(1).begins == "18:30"
    assert day.turn(1).ends == "02:00"