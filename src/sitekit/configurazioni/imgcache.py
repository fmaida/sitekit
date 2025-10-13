import json
from json import JSONDecodeError
from pathlib import Path
from hashlib import md5
from sitekit.settings import BASE_DIR

def __verifica_file_json() -> Path:
    cache_dir = BASE_DIR / ".cache"
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / "images.json"
    cache_file.touch(exist_ok=True)
    return cache_file

# Calcola l'MD5 di un file
# MD5 anche se vecchiotto e non sicuro, basta 
# e avanza per calcolare più velocemente di 
# SHA-1 e SHA-256 se un file è stato 
# modificato oppure no
def __calcola_md5(percorso: Path) -> str | None:
    if not percorso.exists():
        return None
    
    h = md5()
    with open(percorso, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def cache_carica() -> dict:
    cache_file = __verifica_file_json()
    try:
        text = cache_file.read_text(encoding="utf-8").strip()
        return json.loads(text or "{}")
    except JSONDecodeError:
        # File corrotto o non-JSON: riparti pulito
        return {}

def cache_svuota() -> None:
    global CACHE
    cache_file = __verifica_file_json()
    cache_file.unlink(missing_ok=True)    
    CACHE = cache_carica()

def cache_aggiungi(percorso: Path) -> bool:
    """
    Ritorna True se il file è invariato (nessuna conversione da fare),
    oppure False se è nuovo o modificato (serve rigenerare).
    """
    
    percorso = percorso.resolve()
    esito = False
    if percorso.exists():
        trovato = CACHE.get(str(percorso))
        calcolato = __calcola_md5(percorso)
        if not trovato:            
            # Non c'è, lo aggiunge
            CACHE[str(percorso)] = calcolato
        else:
            # C'è già. Vediamo se è lo stesso
            if trovato != calcolato:
                # Non c'è, lo aggiunge
                CACHE[str(percorso)] = calcolato
            else:
                # C'è ed è lo stesso
                esito = True
        
    return esito

def cache_salva() -> None:
    global CACHE

    cache_file = __verifica_file_json()
    tmp = cache_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(CACHE, 
                              ensure_ascii=False, 
                              indent=2), 
                              encoding="utf-8")
    tmp.replace(cache_file)    

CACHE = cache_carica()