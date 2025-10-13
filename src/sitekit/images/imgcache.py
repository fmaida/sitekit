import json
from json import JSONDecodeError
from pathlib import Path
import atexit

from sitekit.settings import settings
from .hash import _calcola_sha1


def svuota() -> None:
    """
    Svuota il file indice
    """
    
    global CACHE

    cache_file = _verifica_file_indice()
    cache_file.unlink(missing_ok=True)    
    CACHE = set()

def verifica_e_aggiungi(input_file: Path, longest_side: int, output_path_folder: Path) -> bool:
    """
    Cerca uno specifico file all'interno della tabella degli hash
    che ha memorizzato nel file json in cache
    Ritorna True se il file è nuovo ed è stato aggiunto all'indice (bisogna rigenerare)
    oppure False se il file era già stato inserito nella cache

    Args:
        input_file: Percorso all'immagine in input
        longest_side: Il lato più lungo dell'immagine
        output_path_folder: Percorso alla cartella di destinazione

    Returns:
        bool:
    """

    global CACHE
    
    input_file = input_file.resolve()    
    if input_file.exists():
        # Il file esiste su disco
        # Calcola il suo SHA-1 e vede 
        hash_calcolato = _calcola_sha1(input_file)
        percorso_file = str(output_path_folder)
        ricercato = (hash_calcolato, longest_side, percorso_file)
        if ricercato in CACHE:
            # Esiste già
            return False
        else:
            # Non esiste ancora
            CACHE.add(ricercato)
            return True        

def salva() -> None:
    global CACHE
        
    cache_file = _verifica_file_indice()
    
    tmp = cache_file.with_suffix(".json.tmp")
    try:
        tmp.write_text(json.dumps(list(CACHE), 
                                  ensure_ascii=False, 
                                  indent=2), 
                                  encoding="utf-8")
        tmp.replace(cache_file)
    except FileNotFoundError:
        print(f"Attenzione: il file temporaneo {tmp} non esiste, cache non salvata.")
    except Exception as e:
        print(f"Errore durante il salvataggio della cache: {e}")

def _verifica_file_indice() -> Path:    
    """
    Verifica che esista un file indice in formato
    .json all'interno della cartella di cache. Se
    non esiste, lo crea

    Returns:
        Path: Il percorso al file indice json
    """
    
    settings.CACHE_DIR.mkdir(exist_ok=True)
    cache_file = settings.CACHE_DIR / "imagesdb.json"
    cache_file.touch(exist_ok=True)
    
    return cache_file


# Si assicura di caricare il file indice in memoria
# per poterlo usare. E se non esiste, lo crea
CACHE = set()
cache_file = _verifica_file_indice()
try:
    text = cache_file.read_text(encoding="utf-8").strip()
    lista = json.loads(text or "[]")
    CACHE = set(tuple(item) for item in lista)
except JSONDecodeError:
    # File corrotto o non-JSON: 
    # per sicurezza riparto pulito, cancellando 
    # tutto quello che poteva aver inserito 
    # dentro CACHE
    CACHE = set()
# Registra nello stack la richiesta di 
# richiamare la funzione salva subito prima
# di killare un processo o subito dopo
# aver premuto CTRL+C
atexit.register(salva)