from collections.abc import Mapping
from typing import Any


def _deep_merge(base: Mapping, altro: Mapping) -> dict:
    """
    Fonde ricorsivamente due dizionari.

    Le mappe annidate vengono unite chiave per chiave; qualsiasi
    altro valore (liste comprese) viene sostituito, non concatenato.
    A parità di chiave vince `altro`.

    Args:
        base: dizionario di partenza.
        altro: dizionario che sovrascrive.

    Returns:
        Un nuovo dizionario, senza modificare gli originali.
    """

    risultato = dict(base)

    for chiave, valore in altro.items():
        precedente = risultato.get(chiave)
        if isinstance(valore, Mapping) and isinstance(precedente, Mapping):
            risultato[chiave] = _deep_merge(precedente, valore)
        else:
            risultato[chiave] = valore

    return risultato


def _annida(segmenti: list[str], valore: Any) -> Any:
    """
    Avvolge un valore nei dizionari indicati dai segmenti.

    Esempio: `_annida(["history", "gallery"], [1, 2])` restituisce
    `{"history": {"gallery": [1, 2]}}`.

    Args:
        segmenti: chiavi dalla più esterna alla più interna.
        valore: valore da innestare in fondo.

    Returns:
        Il valore avvolto nei dizionari, o il valore stesso se non
        ci sono segmenti.
    """

    for segmento in reversed(segmenti):
        valore = {segmento: valore}

    return valore
