from pathlib import Path

from sitekit import cache
from sitekit.settings import settings


def load(*path: str) -> dict | None:
    percorso_completo = settings.CONTENT_DIR.joinpath(*path)
    return cache.load(percorso_completo)