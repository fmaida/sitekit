from collections.abc import Mapping


def _normalize_keys(obj, key_norm=str.lower):
    """
    Rende le chiavi case-insensitive 
    normalizzandole (default: lower()).
    Funziona in profondità su dict e su 
    liste contenenti dict.
    """

    if isinstance(obj, Mapping):
        out = {}
        for k, v in obj.items():
            nk = key_norm(k) if isinstance(k, str) else k
            out[nk] = _normalize_keys(v, key_norm)
        return out
    elif isinstance(obj, list):
        return [_normalize_keys(x, key_norm) for x in obj]
    else:
        return obj