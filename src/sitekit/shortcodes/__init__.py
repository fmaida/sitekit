from .processore import ProcessoreShortcode
from .scoperta import percorsi_template


def renderizza(content_raw: str) -> str:
    """
    Espande gli shortcode in stile Hugo presenti nel testo.

    Punto di ingresso del package: istanzia un processore e gli
    delega l'elaborazione del Markdown grezzo.

    Args:
        content_raw: testo Markdown grezzo con gli shortcode.

    Returns:
        Testo con gli shortcode espansi in HTML.
    """

    processore = ProcessoreShortcode()

    return processore.processa(content_raw)
