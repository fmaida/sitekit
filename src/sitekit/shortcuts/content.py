from pathlib import Path

from sitekit import cache
from sitekit.settings import settings


def load(*path: str) -> dict | None:
    """
    Shortcut di sitekit.cache.load per caricare
    un file di configurazione dalla cartella content
    predefinita
    """

    percorso_completo = settings.CONTENT_DIR.joinpath(*path)
    return cache.load(percorso_completo)