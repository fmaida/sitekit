"""
Individua il pacchetto di un progetto Poetry e i suoi moduli pubblici.
"""

import tomllib
from pathlib import Path

from extractor import extract_module
from hasher import hash_api, hash_file
from models import PackageInfo


SKIP_DIRECTORIES = {
    "__pycache__",
    ".venv",
    "venv",
    "tests",
    "test",
    ".git",
    "build",
    "dist",
}


def _read_pyproject(project_root: Path) -> dict:
    """
    Legge il pyproject.toml del progetto se presente.

    Args:
        project_root: Radice del progetto Poetry.

    Returns:
        Il contenuto del pyproject.toml, dizionario vuoto se assente.
    """
    manifest = project_root / "pyproject.toml"
    if not manifest.is_file():
        return {}

    with manifest.open("rb") as handle:
        return tomllib.load(handle)


def _poetry_section(data: dict) -> dict:
    """
    Estrae la sezione dei metadati dal contenuto del pyproject.toml.

    Supporta sia lo stile `[tool.poetry]` sia lo stile PEP 621 `[project]`.

    Args:
        data: Contenuto gia' deserializzato del pyproject.toml.

    Returns:
        Il dizionario dei metadati del progetto, vuoto se non trovato.
    """
    tool = data.get("tool", {})
    poetry = tool.get("poetry", {})
    if poetry:
        return poetry

    return data.get("project", {})


def _find_package_root(project_root: Path, metadata: dict) -> Path:
    """
    Determina la cartella che contiene il codice sorgente del pacchetto.

    Args:
        project_root: Radice del progetto Poetry.
        metadata: Metadati letti dal pyproject.toml.

    Returns:
        Il percorso della cartella del pacchetto da analizzare.
    """
    packages = metadata.get("packages", [])
    for entry in packages:
        include = entry.get("include", "")
        source = entry.get("from", "")
        candidate = project_root / source / include
        if candidate.is_dir():
            return candidate

    name = str(metadata.get("name", "")).replace("-", "_")
    for candidate in [project_root / "src" / name, project_root / name]:
        if candidate.is_dir():
            return candidate

    return project_root


def _dotted_name(path: Path, package_root: Path) -> str:
    """
    Converte il percorso di un file nel nome puntato del modulo.

    Args:
        path: Percorso del file sorgente.
        package_root: Cartella radice del pacchetto.

    Returns:
        Il nome del modulo in notazione puntata.
    """
    relative = path.relative_to(package_root.parent)
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()

    return ".".join(parts)


def collect_package(project_root: Path) -> PackageInfo:
    """
    Raccoglie l'intera superficie pubblica di un progetto Poetry.

    Args:
        project_root: Radice del progetto da analizzare.

    Returns:
        Un PackageInfo con tutti i moduli pubblici e le loro impronte.
    """
    data = _read_pyproject(project_root)
    metadata = _poetry_section(data)
    package_root = _find_package_root(project_root, metadata)

    package = PackageInfo(
        name=str(metadata.get("name", project_root.name)),
        version=str(metadata.get("version", "")),
        description=str(metadata.get("description", "")),
        root_path=str(package_root.relative_to(project_root)),
    )

    for path in sorted(package_root.rglob("*.py")):
        if any(part in SKIP_DIRECTORIES for part in path.parts):
            continue
        if path.name.startswith("_") and path.name != "__init__.py":
            continue

        module = extract_module(path, project_root, _dotted_name(path, package_root))
        has_surface = (
            module.functions
            or module.classes
            or module.constants
            or module.reexports
        )
        if not has_surface:
            continue

        module.file_sha256 = hash_file(path)
        module.api_sha256 = hash_api(module)
        package.modules.append(module)

    return package
