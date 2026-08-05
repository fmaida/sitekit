"""
Interfaccia a riga di comando per generare e verificare API-CONTRACT.md.

Uso tipico:

    python scripts/generate_contract.py <radice-progetto>
    python scripts/generate_contract.py <radice-progetto> --check
"""

import argparse
import json
import re
import sys
from pathlib import Path

from discovery import collect_package
from renderer import build_manifest, render


MANIFEST_PATTERN = re.compile(
    r"## Manifesto impronte\s*\n\s*```json\s*\n(.*?)\n```",
    re.DOTALL,
)


def _load_manifest(document: Path) -> dict:
    """
    Estrae il manifesto delle impronte da un documento gia' esistente.

    Args:
        document: Percorso del file API-CONTRACT.md da leggere.

    Returns:
        Il manifesto deserializzato, dizionario vuoto se non trovato.
    """
    if not document.is_file():
        return {}

    match = MANIFEST_PATTERN.search(document.read_text(encoding="utf-8"))
    if match is None:
        return {}

    return json.loads(match.group(1))


def _report_drift(stored: dict, current: dict) -> int:
    """
    Confronta il manifesto salvato con quello ricalcolato dal codice.

    Args:
        stored: Manifesto letto dal documento esistente.
        current: Manifesto ricalcolato analizzando i sorgenti.

    Returns:
        Zero se il documento e' allineato, uno se occorre rigenerarlo.
    """
    old_modules = stored.get("modules", {})
    new_modules = current.get("modules", {})
    problems: list[str] = []

    for name, data in new_modules.items():
        previous = old_modules.get(name)
        if previous is None:
            problems.append(f"NUOVO      {name} — modulo assente nel documento")
        elif previous.get("api_sha256") != data.get("api_sha256"):
            problems.append(f"API        {name} — il contratto pubblico e' cambiato")
        elif previous.get("file_sha256") != data.get("file_sha256"):
            print(f"interno    {name} — modifiche interne, contratto invariato")

    for name in old_modules:
        if name not in new_modules:
            problems.append(f"RIMOSSO    {name} — modulo non piu' presente")

    if not problems:
        print(f"Allineato: {len(new_modules)} moduli verificati.")

        return 0

    print("\nDocumento disallineato rispetto al codice:\n")
    for problem in problems:
        print(f"  {problem}")
    print("\nRigenera lanciando lo stesso comando senza --check.")

    return 1


def main() -> int:
    """
    Punto di ingresso dello script a riga di comando.

    Returns:
        Il codice di uscita del processo.
    """
    parser = argparse.ArgumentParser(
        description="Genera o verifica il contratto API di un progetto Poetry."
    )
    parser.add_argument("project", type=Path, help="radice del progetto Poetry")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="percorso del documento (default: <progetto>/API-CONTRACT.md)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verifica la deriva senza riscrivere il documento",
    )
    parser.add_argument(
        "--model",
        default="Claude",
        help="nome del modello da registrare nella sezione Metadata",
    )
    arguments = parser.parse_args()

    project_root = arguments.project.resolve()
    if not project_root.is_dir():
        print(f"Percorso non valido: {project_root}", file=sys.stderr)

        return 2

    document = arguments.output
    if document is None:
        document = project_root / "API-CONTRACT.md"

    package = collect_package(project_root)
    if not package.modules:
        print("Nessun modulo pubblico trovato.", file=sys.stderr)

        return 2

    if arguments.check:
        return _report_drift(_load_manifest(document), build_manifest(package))

    document.write_text(render(package, arguments.model), encoding="utf-8")
    print(f"Scritto {document} — {len(package.modules)} moduli documentati.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
