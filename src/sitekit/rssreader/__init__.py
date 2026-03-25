# v0.2 - 25/03/2026
import feedparser
from . import memos as _memos
from . import wordpress as _wordpress
from ._utils import strip_html


_SOURCES = {
    "memos":     _memos,
    "wordpress": _wordpress,
}


def load(url: str, source: str = "generic", limit: int = 6, body_limit: int = 500) -> list[dict]:
    """
    Scarica e interpreta un feed RSS restituendo una lista di articoli.

    Args:
        url:        URL del feed RSS.
        source:     Tipo di sorgente ("memos", "wordpress").
                    Determina come vengono estratti image e body.
        limit:      Numero massimo di articoli da restituire (default 6).
        body_limit: Lunghezza massima del body in caratteri (default 500).
                    Se il testo è più lungo viene troncato e termina con "…".
                    Passare 0 o None per non troncare.

    Returns:
        Lista di dizionari con chiavi: title, image, body, url.
        Tutti i campi testuali sono testo puro, privi di tag HTML.
    """
    if source not in _SOURCES:
        raise ValueError(
            f"Source '{source}' non supportato. "
            f"Disponibili: {list(_SOURCES.keys())}"
        )

    feed = feedparser.parse(url)
    modulo = _SOURCES[source]

    out = []
    for entry in feed.entries[:limit]:
        # Valori di default comuni a tutti i feed RSS standard
        defaults = {
            "title": strip_html(getattr(entry, "title", "") or ""),
            "url":   getattr(entry, "link", ""),
            "image": None,
            "body":  "",
        }
        # Il connettore sovrascrive/completa con i campi
        # che richiedono logica specifica per la piattaforma
        extra = modulo.importa(entry)
        defaults.update(extra)

        body = defaults.get("body") or ""
        if body_limit and len(body) > body_limit:
            body = body[:body_limit].rstrip() + "…"

        # L'output è sempre e solo queste quattro chiavi,
        # indipendentemente da ciò che il connettore restituisce.
        out.append({
            "title": defaults.get("title") or "",
            "url":   defaults.get("url")   or "",
            "image": defaults.get("image") or None,
            "body":  body,
        })

    return out
