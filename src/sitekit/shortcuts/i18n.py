from pathlib import Path

from sitekit import cache
from sitekit.settings import settings


def load(*path: str) -> dict | None:
    """
    Shortcut di sitekit.cache.load per caricare
    un file di configurazione dalla cartella i18n
    predefinita
    """

    percorso_completo = settings.I18N_DIR.joinpath(*path)
    return cache.load(percorso_completo)