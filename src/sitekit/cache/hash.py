from hashlib import sha1
from pathlib import Path


def _calcola_sha1(
    percorso: Path,
    plugin_paths: list[Path] | None = None,
) -> str | None:
    """
    Calcola l'SHA-1 del contenuto di un file.

    Se vengono passati percorsi di template plugin, aggiunge
    al digest l'mtime_ns di ciascuno (ordinati per percorso),
    così la chiave cambia automaticamente quando un template
    viene modificato su disco.

    Args:
        percorso: Path del file sorgente da hashare.
        plugin_paths: percorsi opzionali dei template plugin
            usati dal file; contribuiscono al digest tramite
            il loro mtime in nanosecondi.

    Returns:
        Stringa esadecimale SHA-1, oppure None se il file
        non esiste.
    """

    if not percorso.exists():
        return None

    h = sha1()
    with open(percorso, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    if plugin_paths:
        for p in sorted(plugin_paths):
            h.update(str(p.stat().st_mtime_ns).encode())

    return h.hexdigest()