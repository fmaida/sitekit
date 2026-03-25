import re
import html as _html


def strip_html(text: str) -> str:
    """
    Rimuove tutti i tag HTML dal testo e decodifica
    le entità HTML (&amp; → &, &lt; → <, &nbsp; → spazio, ecc.).
    Restituisce testo pulito con spazi normalizzati.
    """
    if not text:
        return ""
    # Sostituisce i tag con uno spazio per evitare che le
    # parole adiacenti si incollino (es. <p>Ciao</p><p>mondo</p>)
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decodifica le entità HTML
    text = _html.unescape(text)
    # Normalizza gli spazi bianchi (include \xa0 da &nbsp;)
    return ' '.join(text.split())
