from collections.abc import Mapping
from typing import Any

import markdown

from sitekit import shortcodes


def _normalizza_contenuti(valore: Any) -> Any:
    """
    Uniforma i campi `content` a ogni livello di annidamento.

    Ogni mappa che ha un `content` di tipo stringa senza il
    corrispondente `content_raw` viene trattata come se quel testo
    fosse il corpo di un file: il markdown originale finisce in
    `content_raw` e la resa HTML in `content`. È ciò che rende
    equivalente scrivere il testo nel frontmatter o nel corpo di un
    file di sezione.

    I `content` vuoti vengono rimossi insieme al loro `content_raw`,
    così una sezione senza testo non porta chiavi inutili.

    Args:
        valore: dizionario, lista o valore semplice da normalizzare.

    Returns:
        Una nuova struttura con i campi `content` normalizzati.
    """

    if isinstance(valore, Mapping):
        risultato = {
            chiave: _normalizza_contenuti(interno)
            for chiave, interno in valore.items()
        }

        contenuto = risultato.get("content")
        if isinstance(contenuto, str) and "content_raw" not in risultato:
            risultato["content_raw"] = contenuto
            risultato["content"] = _renderizza(contenuto)

        grezzo = risultato.get("content_raw")
        if isinstance(grezzo, str) and not grezzo.strip():
            risultato.pop("content", None)
            risultato.pop("content_raw", None)

        return risultato

    if isinstance(valore, list):
        return [_normalizza_contenuti(interno) for interno in valore]

    return valore


def _renderizza(testo: str) -> str:
    """
    Converte markdown in HTML con la stessa pipeline della cache.

    Args:
        testo: markdown grezzo, shortcode compresi.

    Returns:
        HTML renderizzato.
    """

    return markdown.markdown(shortcodes.renderizza(testo))
