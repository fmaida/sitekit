import re
from collections.abc import Mapping
from typing import Any

from sitekit.settings import settings
from sitekit.shortcodes.filtri import static


# Attributi che possono puntare a una risorsa del bundle. La
# lookbehind impedisce di agganciare attributi come "data-src",
# che i template dei plugin risolvono per conto loro.
_RIFERIMENTO = re.compile(
    r"""(?<![-\w])((?:src|href)\s*=\s*)(["'])(.*?)\2""",
    re.IGNORECASE,
)

# Schemi tipo "http:", "mailto:", "data:".
_SCHEMA = re.compile(r"\A[a-zA-Z][a-zA-Z0-9+.\-]*:")


def _ancora_asset(valore: Any, slug: str) -> Any:
    """
    Ancora i riferimenti relativi alla root del page bundle.

    Un `[foto](foto.jpg)` scritto in un file markdown del bundle
    punta sempre alla root del bundle, anche quando il file sta in
    una cartella-lingua: `pagina/en/index.md` che cita `foto.jpg`
    intende `pagina/foto.jpg`, mai `pagina/en/foto.jpg`.

    La riscrittura tocca solo gli `src`/`href` dell'HTML già
    renderizzato (le chiavi `content`); `content_raw` e i valori del
    frontmatter restano quelli scritti dall'autore.

    Args:
        valore: dizionario, lista o valore semplice da riscrivere.
        slug: nome del page bundle. Se vuoto (nessun bundle) i
            riferimenti vengono lasciati invariati.

    Returns:
        Una nuova struttura con i riferimenti relativi riscritti.
    """

    if not slug:
        return valore

    if isinstance(valore, Mapping):
        risultato = {}
        for chiave, interno in valore.items():
            if chiave == "content" and isinstance(interno, str):
                risultato[chiave] = _riscrivi(interno, slug)
            else:
                risultato[chiave] = _ancora_asset(interno, slug)
        return risultato

    if isinstance(valore, list):
        return [_ancora_asset(interno, slug) for interno in valore]

    return valore


def _riscrivi(html: str, slug: str) -> str:
    """
    Sostituisce i riferimenti relativi di un frammento HTML.

    Args:
        html: HTML renderizzato.
        slug: nome del page bundle.

    Returns:
        HTML con gli `src`/`href` relativi trasformati in URL
        assoluti sotto la cartella asset del bundle.
    """

    prefisso = settings.BUNDLE_ASSETS_URL.format(slug=slug).strip("/")

    def sostituisci(match: re.Match) -> str:
        percorso = match.group(3)
        if not _e_relativo(percorso):
            return match.group(0)

        pulito = percorso[2:] if percorso.startswith("./") else percorso
        url = static(f"{prefisso}/{pulito}")

        return f"{match.group(1)}{match.group(2)}{url}{match.group(2)}"

    return _RIFERIMENTO.sub(sostituisci, html)


def _e_relativo(percorso: str) -> bool:
    """
    Dice se un riferimento va ancorato alla root del bundle.

    Args:
        percorso: valore di un attributo src o href.

    Returns:
        False per URL assoluti, percorsi che iniziano con "/",
        ancore, query e schemi come "mailto:"; True altrimenti.
    """

    if not percorso:
        return False

    if percorso.startswith(("/", "#", "?")):
        return False

    return _SCHEMA.match(percorso) is None
