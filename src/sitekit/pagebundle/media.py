import shutil
from pathlib import Path

from sitekit import images
from sitekit.assets import percorsi
from sitekit.settings import settings


# Immagini: passano per images.copy, che genera i breakpoint.
TIPI_IMMAGINE = (".jpg", ".jpeg", ".png")

# File di contenuto: sono la pagina, non un suo asset.
TIPI_IGNORATI = (".md", ".markdown", ".yaml", ".yml", ".json")


def _sottopercorso(slug: str) -> str:
    """
    Percorso degli asset di un bundle, relativo alla radice assets.

    Args:
        slug: nome del page bundle.

    Returns:
        Ad esempio "images/primo-post".
    """

    return f"{settings.BUNDLE_ASSETS_SUBDIR}/{slug}".strip("/")


def destinazione(slug: str) -> Path:
    """
    Cartella su disco in cui finiscono gli asset del bundle.

    Args:
        slug: nome del page bundle.

    Returns:
        Path dentro CACHE_DIR/assets, creata se non esiste.
    """

    return percorsi.destinazione(_sottopercorso(slug))


def url(slug: str) -> str:
    """
    URL pubblico degli asset del bundle.

    Args:
        slug: nome del page bundle.

    Returns:
        Ad esempio "/assets/images/primo-post".
    """

    return percorsi.url(_sottopercorso(slug))


def copia(cartella: Path, slug: str) -> str | None:
    """
    Converte e copia gli asset di un page bundle.

    Le immagini passano per `images.copy`, che genera i quattro
    breakpoint in AVIF, WebP e JPEG dentro una sottocartella con lo
    stem del file. I file di contenuto vengono ignorati, tutto il
    resto viene copiato tal quale.

    Args:
        cartella: root del page bundle.
        slug: nome del page bundle, che dà il nome alla cartella di
            destinazione.

    Returns:
        Lo stem del primo file immagine che contiene "_cover" nel
        nome, oppure None se non ce n'è nessuno.
    """

    if not slug:
        return None

    cartella_destinazione = destinazione(slug)
    base_url = url(slug)
    cover = None

    for elemento in sorted(cartella.glob("*")):
        if not elemento.is_file():
            continue

        suffisso = elemento.suffix.lower()

        if suffisso in TIPI_IMMAGINE:
            images.copy(
                source_image=elemento,
                destination_folder=cartella_destinazione,
                aspect_ratio=settings.BUNDLE_ASPECT_RATIO,
                base_url=base_url,
            )
            if cover is None and "_cover" in elemento.stem:
                cover = elemento.stem
        elif suffisso not in TIPI_IGNORATI:
            _copia_se_serve(elemento, cartella_destinazione / elemento.name)

    return cover


def _copia_se_serve(origine: Path, destinazione_file: Path) -> None:
    """
    Copia un file solo se la destinazione non è già aggiornata.

    Args:
        origine: file sorgente.
        destinazione_file: percorso di destinazione.
    """

    if destinazione_file.exists():
        stat_origine = origine.stat()
        stat_destinazione = destinazione_file.stat()
        if (
            stat_origine.st_size == stat_destinazione.st_size
            and stat_origine.st_mtime <= stat_destinazione.st_mtime
        ):
            return

    shutil.copy2(origine, destinazione_file)
