import re
from pathlib import Path

import yaml

from sitekit import cache
from sitekit.cache.normalize import _normalize_keys


# Blocco frontmatter delimitato da --- a inizio file.
_BLOCCO = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n(.*))?\Z", re.DOTALL)


def _carica_valore(percorso: Path) -> dict | list:
    """
    Carica un file della pagina nel valore che rappresenta.

    Nel caso normale delega a `cache.load`, così cache su disco e in
    RAM, plugin e shortcode continuano a funzionare. Se però il
    frontmatter è una **sequenza** YAML anziché una mappa, il valore
    della sezione è la sequenza stessa: python-frontmatter in quel
    caso scarterebbe i dati, quindi il file viene letto a parte.

    Args:
        percorso: Path del file markdown da caricare.

    Returns:
        Il dizionario prodotto da `cache.load`, oppure la lista
        dichiarata nel frontmatter.

    Raises:
        ValueError: se un file con frontmatter a sequenza ha anche un
            corpo markdown non vuoto, perché non ci sarebbe posto dove
            metterlo.
    """

    sequenza = _leggi_sequenza(percorso)
    if sequenza is not None:
        return sequenza

    return cache.load(percorso)


def _leggi_sequenza(percorso: Path) -> list | None:
    """
    Restituisce il frontmatter del file se è una sequenza YAML.

    Args:
        percorso: Path del file markdown da esaminare.

    Returns:
        La lista dichiarata nel frontmatter, o None se il
        frontmatter è una mappa (o manca del tutto).

    Raises:
        ValueError: se al frontmatter a sequenza segue un corpo
            markdown non vuoto.
    """

    testo = percorso.read_text(encoding="utf-8")

    match = _BLOCCO.match(testo)
    if match is None:
        return None

    blocco = match.group(1)
    corpo = match.group(2) or ""

    # Sniff economico: solo una sequenza YAML comincia con "- ".
    prima_riga = next(
        (riga for riga in blocco.splitlines() if riga.strip()),
        "",
    )
    if not prima_riga.startswith("- "):
        return None

    dati = yaml.safe_load(blocco)
    if not isinstance(dati, list):
        return None

    if corpo.strip():
        raise ValueError(
            f"Il file ha un frontmatter a sequenza e non può avere "
            f"anche un corpo markdown: \"{percorso}\""
        )

    return _normalize_keys(dati)
