"""
Calcola le impronte sha-256 usate per rilevare la deriva del contratto.

Vengono prodotte due impronte distinte per ogni modulo:

- `file_sha256` copre l'intero file e cambia a ogni modifica, anche interna.
- `api_sha256` copre solo cio' che il documento riproduce davvero, cioe'
  firme, tipi e docstring pubbliche. Se questa impronta coincide, la sezione
  del documento relativa al modulo e' ancora accurata.
"""

import hashlib
from pathlib import Path

from models import ClassInfo, FunctionInfo, ModuleInfo


def hash_file(path: Path) -> str:
    """
    Calcola lo sha-256 del contenuto grezzo di un file.

    Args:
        path: Percorso del file da leggere in modalita' binaria.

    Returns:
        L'impronta esadecimale del file.
    """
    digest = hashlib.sha256()
    digest.update(path.read_bytes())

    return digest.hexdigest()


def _canonical_function(function: FunctionInfo, prefix: str = "") -> list[str]:
    """
    Riduce una funzione a righe canoniche indipendenti dalla formattazione.

    Args:
        function: Descrizione della funzione da normalizzare.
        prefix: Prefisso opzionale, usato per i metodi di una classe.

    Returns:
        Elenco di righe canoniche che rappresentano la funzione.
    """
    parts: list[str] = []
    for parameter in function.parameters:
        parts.append(
            f"{parameter.prefix}{parameter.name}:"
            f"{parameter.annotation}={parameter.default}"
        )

    signature = ",".join(parts)
    flags = f"{function.is_async}{function.is_property}{function.is_static}"
    lines = [
        f"fn:{prefix}{function.name}({signature})->{function.returns}|{flags}",
        f"doc:{prefix}{function.name}:{' '.join(function.docstring.split())}",
    ]

    return lines


def _canonical_class(klass: ClassInfo) -> list[str]:
    """
    Riduce una classe e i suoi membri pubblici a righe canoniche.

    Args:
        klass: Descrizione della classe da normalizzare.

    Returns:
        Elenco di righe canoniche che rappresentano la classe.
    """
    lines = [
        f"class:{klass.name}({','.join(klass.bases)})",
        f"doc:{klass.name}:{' '.join(klass.docstring.split())}",
    ]

    for attribute in klass.attributes:
        lines.append(
            f"attr:{klass.name}.{attribute.name}:"
            f"{attribute.annotation}={attribute.default}"
        )

    for method in klass.methods:
        lines.extend(_canonical_function(method, prefix=f"{klass.name}."))

    return lines


def canonical_api(module: ModuleInfo) -> str:
    """
    Produce la rappresentazione canonica dell'API pubblica di un modulo.

    La rappresentazione ignora ordine di scrittura, spaziatura e commenti,
    cosi' che un semplice riordino del codice non generi un falso allarme.

    Args:
        module: Descrizione del modulo da normalizzare.

    Returns:
        Una stringa deterministica che rappresenta la sola API pubblica.
    """
    lines = [f"module:{module.dotted_name}"]
    lines.append(f"doc:module:{' '.join(module.docstring.split())}")

    for name in module.reexports:
        lines.append(f"reexport:{name}")

    for constant in module.constants:
        lines.append(f"const:{constant.name}:{constant.annotation}={constant.value}")

    for function in module.functions:
        lines.extend(_canonical_function(function))

    for klass in module.classes:
        lines.extend(_canonical_class(klass))

    return "\n".join(sorted(lines))


def hash_api(module: ModuleInfo) -> str:
    """
    Calcola lo sha-256 della sola superficie pubblica di un modulo.

    Args:
        module: Descrizione del modulo da valutare.

    Returns:
        L'impronta esadecimale dell'API pubblica.
    """
    digest = hashlib.sha256()
    digest.update(canonical_api(module).encode("utf-8"))

    return digest.hexdigest()
