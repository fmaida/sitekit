from sitekit.assets import percorsi


def asset(percorso: str) -> str:
    """
    Risolve un percorso relativo rispetto alla cartella assets.

    Vale per qualsiasi risorsa servita da assets (immagini, audio,
    video, css, javascript, font). Gli URL assoluti (http, https o
    protocol-relative) vengono restituiti invariati.

    Args:
        percorso: percorso della risorsa relativo alla radice degli
            asset, ad esempio "images/immagine/immagine__800.jpg".

    Returns:
        URL completo con il prefisso ASSETS_URL, ad esempio
        "/assets/images/immagine/immagine__800.jpg".
    """

    if percorso.startswith(("http://", "https://", "//")):
        return percorso

    return percorsi.url(percorso)


# I template dei plugin scritti finora usano il nome "static":
# resta valido come alias di "asset".
static = asset
