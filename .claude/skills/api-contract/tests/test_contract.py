"""
Test di regressione per l'estrazione dell'API e il calcolo delle impronte.
"""

import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from extractor import extract_module
from hasher import hash_api


SOURCE = '''
"""
Modulo di prova.
"""

MAX_RETRIES: int = 3


def public_call(name: str, retries: int = MAX_RETRIES) -> bool:
    """
    Fa qualcosa di pubblico.
    """

    return True


def _private_call() -> None:
    """
    Non deve comparire nel contratto.
    """
'''


@pytest.fixture()
def module_path(tmp_path: Path) -> Path:
    """
    Scrive il sorgente di prova su disco e ne restituisce il percorso.

    Args:
        tmp_path: Cartella temporanea fornita da pytest.

    Returns:
        Il percorso del file sorgente creato.
    """
    path = tmp_path / "sample.py"
    path.write_text(SOURCE, encoding="utf-8")

    return path


def test_estrae_solo_i_nomi_pubblici(module_path: Path) -> None:
    """
    Verifica che i nomi con underscore iniziale restino fuori.
    """
    module = extract_module(module_path, module_path.parent, "sample")
    names = [function.name for function in module.functions]

    assert names == ["public_call"]


def test_estrae_le_costanti_annotate(module_path: Path) -> None:
    """
    Verifica che le costanti in maiuscolo finiscano nel contratto.
    """
    module = extract_module(module_path, module_path.parent, "sample")

    assert module.constants[0].name == "MAX_RETRIES"


def test_impronta_ignora_il_corpo_delle_funzioni(
    tmp_path: Path, module_path: Path
) -> None:
    """
    Verifica che cambiare solo l'implementazione non cambi api_sha256.
    """
    original = extract_module(module_path, module_path.parent, "sample")
    modified_path = tmp_path / "modified.py"
    modified_path.write_text(
        SOURCE.replace("    return True", "    return bool(name)"),
        encoding="utf-8",
    )
    modified = extract_module(modified_path, tmp_path, "sample")

    assert hash_api(original) == hash_api(modified)


def test_impronta_cambia_se_cambia_la_firma(
    tmp_path: Path, module_path: Path
) -> None:
    """
    Verifica che aggiungere un parametro pubblico cambi api_sha256.
    """
    original = extract_module(module_path, module_path.parent, "sample")
    changed_path = tmp_path / "changed.py"
    changed_path.write_text(
        SOURCE.replace("name: str,", "name: str, timeout: int = 5,"),
        encoding="utf-8",
    )
    changed = extract_module(changed_path, tmp_path, "sample")

    assert hash_api(original) != hash_api(changed)
