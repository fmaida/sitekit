import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from sitekit.images import PictureClass
from . import media


# Un tag <img> intero: per le immagini non basta riscrivere l'URL,
# il tag va sostituito dal <picture> con tutti i breakpoint.
_TAG_IMG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)

# Attributi che possono puntare a una risorsa del bundle. La
# lookbehind impedisce di agganciare attributi come "data-src",
# che i template dei plugin risolvono per conto loro.
_RIFERIMENTO = re.compile(
    r"""(?<![-\w])((?:src|href)\s*=\s*)(["'])(.*?)\2""",
    re.IGNORECASE,
)

_ALT = re.compile(r"""(?<![-\w])alt\s*=\s*(["'])(.*?)\1""", re.IGNORECASE)

# Schemi tipo "http:", "mailto:", "data:".
_SCHEMA = re.compile(r"\A[a-zA-Z][a-zA-Z0-9+.\-]*:")

# La versione più grande generata da images.copy, quella che ha
# senso aprire seguendo un link a un'immagine.
_BREAKPOINT_GRANDE = 1600


def _ancora_asset(valore: Any, slug: str, cartella: Path) -> Any:
    """
    Ancora i riferimenti relativi alla root del page bundle.

    Un `[foto](foto.jpg)` scritto in un file markdown del bundle
    punta sempre alla root del bundle, anche quando il file sta in
    una cartella-lingua: `pagina/en/index.md` che cita `foto.jpg`
    intende `pagina/foto.jpg`, mai `pagina/en/foto.jpg`.

    La riscrittura segue ciò che `media.copia` ha davvero scritto su
    disco: le immagini diventano un tag `<picture>` con tutti i
    breakpoint, gli altri file copiati diventano un URL sotto la
    cartella asset del bundle, i file di contenuto restano com'erano.

    Tocca solo l'HTML già renderizzato (le chiavi `content`);
    `content_raw` e i valori del frontmatter restano quelli scritti
    dall'autore.

    Args:
        valore: dizionario, lista o valore semplice da riscrivere.
        slug: nome del page bundle. Se vuoto (nessun bundle) i
            riferimenti vengono lasciati invariati.
        cartella: root del page bundle, per sapere quali file
            esistono davvero.

    Returns:
        Una nuova struttura con i riferimenti relativi riscritti.
    """

    if not slug:
        return valore

    if isinstance(valore, Mapping):
        risultato = {}
        for chiave, interno in valore.items():
            if chiave == "content" and isinstance(interno, str):
                risultato[chiave] = _riscrivi(interno, slug, cartella)
            else:
                risultato[chiave] = _ancora_asset(interno, slug, cartella)
        return risultato

    if isinstance(valore, list):
        return [_ancora_asset(interno, slug, cartella) for interno in valore]

    return valore


def _riscrivi(html: str, slug: str, cartella: Path) -> str:
    """
    Riscrive i riferimenti di un frammento HTML renderizzato.

    Prima i tag `<img>`, che vengono sostituiti in blocco dal
    `<picture>`; poi gli altri `src`/`href` rimasti. L'ordine conta:
    il markup prodotto dal `<picture>` contiene URL già assoluti,
    che la seconda passata lascia stare.

    Args:
        html: HTML renderizzato.
        slug: nome del page bundle.
        cartella: root del page bundle.

    Returns:
        HTML con i riferimenti agli asset del bundle risolti.
    """

    html = _TAG_IMG.sub(lambda match: _su_img(match, slug, cartella), html)

    def sostituisci(match: re.Match) -> str:
        url = _url_di(match.group(3), slug, cartella)
        if url is None:
            return match.group(0)

        return f"{match.group(1)}{match.group(2)}{url}{match.group(2)}"

    return _RIFERIMENTO.sub(sostituisci, html)


def _su_img(match: re.Match, slug: str, cartella: Path) -> str:
    """
    Sostituisce un tag <img> con il <picture> corrispondente.

    Vale solo se l'immagine è un file del bundle passato per
    `images.copy`: negli altri casi il tag resta com'è e ci pensa la
    passata sugli attributi.

    Args:
        match: il tag <img> intero.
        slug: nome del page bundle.
        cartella: root del page bundle.

    Returns:
        Il markup `<picture>`, oppure il tag originale.
    """

    tag = match.group(0)

    riferimento = _RIFERIMENTO.search(tag)
    if riferimento is None:
        return tag

    sorgente = _file_del_bundle(riferimento.group(3), cartella)
    if sorgente is None or sorgente.suffix.lower() not in media.TIPI_IMMAGINE:
        return tag

    alt = _ALT.search(tag)
    stem = sorgente.stem

    immagine = PictureClass(
        folder=media.destinazione(slug) / stem,
        alt=alt.group(2) if alt else "",
        base_url=f"{media.url(slug)}/{stem}",
    )

    return str(immagine)


def _url_di(percorso: str, slug: str, cartella: Path) -> str | None:
    """
    URL pubblico di un riferimento relativo, se ne ha uno.

    Args:
        percorso: valore di un attributo src o href.
        slug: nome del page bundle.
        cartella: root del page bundle.

    Returns:
        L'URL da sostituire, oppure None se il riferimento va
        lasciato invariato.
    """

    sorgente = _file_del_bundle(percorso, cartella)
    if sorgente is None:
        return None

    suffisso = sorgente.suffix.lower()
    base = media.url(slug)

    if suffisso in media.TIPI_IMMAGINE:
        # Un link a un'immagine punta al breakpoint più grande: il
        # file con il nome originale non viene mai scritto.
        stem = sorgente.stem
        return f"{base}/{stem}/{stem}__{_BREAKPOINT_GRANDE}.jpg"

    if suffisso in media.TIPI_IGNORATI:
        # Sono file di contenuto, non asset: nessuno li ha copiati.
        return None

    return f"{base}/{sorgente.name}"


def _file_del_bundle(percorso: str, cartella: Path) -> Path | None:
    """
    Risolve un riferimento nel file del bundle che nomina.

    I riferimenti relativi puntano sempre alla root del bundle,
    qualunque sia il file che li contiene. Solo i file che stanno
    nella root vengono considerati: `media.copia` guarda lì, e
    riscrivere un riferimento a `video/clip.mp4` produrrebbe un URL
    verso un file che nessuno ha copiato.

    Args:
        percorso: valore di un attributo src o href.
        cartella: root del page bundle.

    Returns:
        Il Path del file, oppure None se il riferimento non è
        relativo, punta a una sottocartella, o non corrisponde a
        nessun file nella root del bundle.
    """

    if not percorso or percorso.startswith(("/", "#", "?")):
        return None

    if _SCHEMA.match(percorso) is not None:
        return None

    pulito = percorso[2:] if percorso.startswith("./") else percorso
    pulito = pulito.split("?", 1)[0].split("#", 1)[0]

    if "/" in pulito or "\\" in pulito:
        return None

    candidato = cartella / pulito
    if not candidato.is_file():
        return None

    return candidato
