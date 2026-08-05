from pathlib import Path

from sitekit.settings import settings


def _segmenti(sottopercorso: str | Path) -> list[str]:
    """
    Scompone un sottopercorso in segmenti, ignorando separatori
    ridondanti e i riferimenti alla cartella corrente.

    Args:
        sottopercorso: percorso relativo, con separatori POSIX o
            nativi.

    Returns:
        Lista di segmenti, vuota se il sottopercorso è vuoto.
    """

    if not sottopercorso:
        return []

    return [
        segmento
        for segmento in Path(sottopercorso).as_posix().split("/")
        if segmento and segmento != "."
    ]


def cartella_generati() -> Path:
    """
    Radice degli asset generati, dentro la cache.

    È un mirror parziale di ASSETS_DIR: ci finisce solo ciò che la
    libreria produce (immagini convertite, file copiati dai page
    bundle), così una `assets.build(pulisci=True)` può azzerare la
    cartella finale senza costringere a riconvertire tutto.

    Returns:
        Path di CACHE_DIR / "assets".
    """

    return settings.CACHE_DIR / "assets"


def destinazione(sottopercorso: str | Path = "") -> Path:
    """
    Percorso su disco in cui scrivere un asset generato.

    È quello che si passa come `destination_folder` a
    `images.copy`. La cartella viene creata se non esiste.

    Args:
        sottopercorso: percorso relativo alla radice degli asset,
            ad esempio "images/chi-siamo".

    Returns:
        Path assoluta dentro CACHE_DIR / "assets".
    """

    percorso = cartella_generati().joinpath(*_segmenti(sottopercorso))
    percorso.mkdir(parents=True, exist_ok=True)

    return percorso


def url(sottopercorso: str | Path = "") -> str:
    """
    URL pubblico corrispondente a un sottopercorso degli asset.

    `destinazione()` e `url()` sono le due facce dello stesso
    percorso: usarle in coppia è ciò che impedisce a dove si scrive
    e a cosa si stampa di divergere.

    Args:
        sottopercorso: percorso relativo alla radice degli asset,
            ad esempio "images/chi-siamo".

    Returns:
        URL assoluto, ad esempio "/assets/images/chi-siamo".
    """

    base = settings.ASSETS_URL.rstrip("/")
    segmenti = _segmenti(sottopercorso)

    if not segmenti:
        return base or "/"

    return base + "/" + "/".join(segmenti)
