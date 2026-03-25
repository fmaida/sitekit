import re
from ._utils import strip_html


def importa(entry) -> dict:
    """
    Estrae body e image da una entry feedparser di un feed WordPress.

    WordPress pubblica il testo completo in content:encoded (entry.content),
    con fallback sull'excerpt in entry.summary.
    L'immagine in evidenza si trova tipicamente in media:content,
    media:thumbnail, negli enclosures, oppure come prima <img> nel body.
    """
    # ── Body ──────────────────────────────────────────────────────────────────
    body_html = ""
    content = getattr(entry, "content", [])
    if content:
        body_html = content[0].get("value", "")
    if not body_html:
        body_html = getattr(entry, "summary", "") or ""

    body = strip_html(body_html)

    # ── Immagine ──────────────────────────────────────────────────────────────
    # Cascata: media:content → media:thumbnail → enclosures → prima <img>
    image = None

    media = getattr(entry, "media_content", [])
    if media:
        image = media[0].get("url")

    if not image:
        thumbnails = getattr(entry, "media_thumbnail", [])
        if thumbnails:
            image = thumbnails[0].get("url")

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
        "body":  body,
        "image": image,
    }
