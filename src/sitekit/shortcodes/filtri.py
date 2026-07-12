from sitekit.settings import settings


def static(percorso: str) -> str:
    """
    Risolve un percorso relativo rispetto alla cartella static.

    Vale per qualsiasi asset servito da static (immagini, audio,
    video, css, javascript). Gli URL assoluti (http, https o
    protocol-relative) vengono restituiti invariati.

    Args:
        percorso: percorso dell'asset relativo a static, ad
            esempio "/images/immagine/immagine__800.jpg".

    Returns:
        URL completo con il prefisso STATIC_CONTENT, ad esempio
        "/static/images/immagine/immagine__800.jpg".
    """

    if percorso.startswith(("http://", "https://", "//")):
        return percorso

    base = settings.STATIC_CONTENT.rstrip("/")
    resto = percorso.lstrip("/")

    return f"{base}/{resto}"
