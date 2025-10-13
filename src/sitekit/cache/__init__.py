from pathlib import Path

import frontmatter
import markdown
import yaml
import json
import pickle

from sitekit.settings import CACHE_DIR
from .hash import _calcola_sha1
from .normalize import _normalize_keys
from . import ram


# set globale con i file usati in questa run
_used_cache_files: set[str] = set()

def load(input_file: Path) -> dict | None:
    input_file = Path(input_file)
    if not (input_file.exists() and input_file.is_file()):
        raise FileNotFoundError(f"File non trovato: \"{input_file}\"")

    dati = None
    checksum_origine = _calcola_sha1(input_file)
    file_cache = CACHE_DIR / (checksum_origine + ".pickle")
    if file_cache.exists():
        # Restituisce il file scongelato
        dati = _scongela_file(file_cache)            
    if dati is None:
        ext = input_file.suffix.lower() 
        if ext == ".json":
            dati = _carica_json(input_file)
        elif ext in (".yaml", ".yml"):
            dati = _carica_yaml(input_file)
        elif ext in (".md", ".markdown"):
            dati = _carica_frontmatter(input_file)
        else:
            raise ValueError(f"Non supportato: \"{input_file}\"")
        
        # congela il file
        _congela_file(file_cache, dati)

    # segna il file come usato
    _used_cache_files.add(file_cache.name)
    return dati

def _scongela_file(file_cache) -> dict | None:
    try:
        dati = ram.carica(file_cache.name)        
        if dati is None:
            # Non c'è in RAM. Lo carica da disco
            with open(file_cache, "rb") as f:
                dati = pickle.load(f)
            # Popola la RAM cache con l'oggetto già pronto
            ram.salva(file_cache.name, dati)
    except Exception:
        # La cache è corrotta
        dati = None
    
    return dati
          
def _congela_file(file_cache: Path, dati: dict):
    temp = file_cache.parent / (file_cache.name + ".tmp")
    data_bytes = pickle.dumps(dati, protocol=pickle.HIGHEST_PROTOCOL)
    with open(temp, "wb") as f:
        f.write(data_bytes)     
    temp.replace(file_cache)
    # In RAM salvi direttamente l'oggetto, non i bytes
    ram.salva(file_cache.name, dati)

    
def _carica_json(input_file: Path) -> dict:
    with input_file.open("r", encoding="utf-8") as f:
        return json.load(f)

def _carica_yaml(input_file: Path) -> dict:    
    with input_file.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _carica_frontmatter(input_file: Path) -> dict:
    """
    Carica un file frontmatter
    con YAML + Markdown
    """
    
    data = frontmatter.load(input_file)
    temp = {}
    if data.metadata:
        temp |= _normalize_keys(data.metadata)
    temp["content_raw"] = data.content or ""
    temp["content"] = markdown.markdown(temp["content_raw"])
    return temp

def clean():
    """
    Ripulisce la cartella di cache,
    Cancellando tutti i file non utilizzati
    durante l'esecuzione
    """

    # Rimuove tutti i file con estensione
    # .pickle che non sono stati utilizzati
    for file_cache in CACHE_DIR.glob("*.pickle"):
        if file_cache.name not in _used_cache_files:
            try:
                file_cache.unlink()
            except Exception:
                pass
    
    # Rimuove eventuali file con estensione
    # .tmp rimasti orfani
    for tmp in CACHE_DIR.glob("*.tmp"):
        try:
            tmp.unlink()
        except Exception:
            pass


# Inizializzazione
# Giusto per essere certi che CACHE_DIR esista
CACHE_DIR.mkdir(parents=True, exist_ok=True)