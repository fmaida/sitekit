import re


_ATTRIBUTO = re.compile(r"""([\w-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""")


def analizza_attributi(testo: str) -> dict[str, str]:
    """
    Estrae le coppie chiave="valore" dalla parte attributi di
    uno shortcode.

    Accetta sia virgolette doppie sia singole. Una stringa vuota
    o priva di attributi produce un dizionario vuoto.

    Args:
        testo: porzione di shortcode con gli attributi, ad
            esempio 'url="/img.jpg" alt="Gigetto"'.

    Returns:
        Dizionario degli attributi trovati, nell'ordine di
        comparsa.
    """

    attributi: dict[str, str] = {}
    for match in _ATTRIBUTO.finditer(testo):
        nome = match.group(1)
        valore = match.group(2)
        if valore is None:
            valore = match.group(3)
        attributi[nome] = valore

    return attributi
