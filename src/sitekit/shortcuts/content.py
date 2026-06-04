from pathlib import Path

from sitekit import cache
from sitekit.settings import settings


def load(*path: str | Path) -> dict | None:
    """
    Shortcut di sitekit.cache.load per caricare
    un file di configurazione dalla cartella content
    predefinita.

    Accetta stringhe e istanze di Path. Se viene passata una Path
    assoluta, viene usata direttamente senza prefissare CONTENT_DIR.
    """

    percorso_completo = settings.CONTENT_DIR.joinpath(*path)

    return cache.load(percorso_completo)