import re
from ._utils import strip_html


def importa(entry) -> dict:
    """
    Estrae body e image da una entry feedparser di un feed Memos.

    Memos spesso non compila il campo title (o lo lascia vuoto):
    in quel caso si usano le prime parole del body come titolo.
    Le immagini sono tipicamente in <enclosure> (jpeg/png/gif);
    eventuali enclosure video/* o audio/* vengono ignorati.
    """
    # ── Body ──────────────────────────────────────────────────────────────────
    # feedparser espone content:encoded in entry.content (lista di dict),
    # con fallback su entry.summary
    body_html = ""
    content = getattr(entry, "content", [])
    if content:
        body_html = content[0].get("value", "")
    if not body_html:
        body_html = getattr(entry, "summary", "") or ""

    body = strip_html(body_html)

    # ── Titolo ────────────────────────────────────────────────────────────────
    # Memos di solito non ha un titolo strutturato: il campo title
    # del feed è spesso vuoto o assente. Se manca, si derivano le
    # prime 8 parole dal body.
    title = strip_html(getattr(entry, "title", "") or "")
    if not title and body:
        words = body.split()
        title = " ".join(words[:8]) + ("…" if len(words) > 8 else "")

    # ── Immagine ──────────────────────────────────────────────────────────────
    # Memos espone le immagini allegate principalmente tramite <enclosure>.
    # Cascata: media:content → enclosures image/* → prima <img> nel body.
    # Gli enclosure di tipo video/* o audio/* vengono ignorati.
    image = None

    media = getattr(entry, "media_content", [])
    if media:
        image = media[0].get("url")

    if not image:
        for enc in getattr(entry, "enclosures", []):
            if enc.get("type", "").startswith("image/"):
                image = enc.get("href")
                break

    if not image and body_html:
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', body_html, re.IGNORECASE)
        if match:
            image = match.group(1)

    return {
        "title": title,
        "body":  body,
        "image": image,
    }
