from babel.dates import get_day_names
from sitekit.settings import settings
import json


def localizza_stringhe(lingua):
    t = {}
    try:
        with open(settings.I18N_DIR / f"{lingua}.json", "r", encoding="utf-8") as f:
            dati = json.load(f)
    except FileNotFoundError:
        # La lingua non è supportata,
        # carica la lingua di default (inglese)
        lingua = "en"
        with open(settings.I18N_DIR / f"{lingua}.json", "r", encoding="utf-8") as f:
            dati = json.load(f)

    for chiave, valore in dati.items():
        t[chiave] = valore

    # Giorni della settimana da Lunedì a Domenica (Babel: 0 = Lunedì)
    giorni = get_day_names('wide', locale=lingua)
    t["giorni"] = [giorni[i] for i in range(7)]

    return t
