import re
from pathlib import Path

import frontmatter

from sitekit.settings import settings


_NOMI = re.compile(r"\{\{[<%]\s*([\w-]+)")


def percorsi_template(input_file: Path) -> list[Path]:
    """
    Trova i template usati dagli shortcode inline di un file.

    Serve alla cache: includendo questi template nel digest, la
    chiave cambia quando uno di essi viene modificato. I template
    inesistenti vengono ignorati, coerentemente con il rendering
    tollerante del processore.

    Args:
        input_file: Path del file Markdown da analizzare.

    Returns:
        Lista di Path ai template degli shortcode, senza
        duplicati, nell'ordine di prima comparsa.
    """

    dati = frontmatter.load(input_file)
    contenuto = dati.content or ""

    percorsi: list[Path] = []
    visti: set[str] = set()
    for nome in _NOMI.findall(contenuto):
        if nome == "end" or nome in visti:
            continue
        visti.add(nome)
        template = settings.PLUGINS_DIR / f"{nome}.jinja2"
        if template.exists():
            percorsi.append(template)

    return percorsi
