from pathlib import Path

import frontmatter
import markdown
import yaml
import json
import pickle

from sitekit.settings import settings
from .hash import _calcola_sha1
from .normalize import _normalize_keys
from .plugins import _renderizza_plugin
from . import ram


# set globale con i file usati in questa run
_used_cache_files: set[str] = set()

def _estrai_plugin_paths(input_file: Path) -> list[Path]:
    """
    Legge il frontmatter di un file markdown e restituisce
    i percorsi univoci dei template plugin dichiarati.

    Args:
        input_file: Path del file markdown da analizzare.

    Returns:
        Lista di Path ai template plugin, senza duplicati,
        nell'ordine di prima comparsa nel frontmatter.

    Raises:
        FileNotFoundError: se un template plugin dichiarato
            non esiste in PLUGINS_DIR.
    """

    data = frontmatter.load(input_file)
    plugins_raw = data.metadata.get("plugins") or []

    seen: set[Path] = set()
    paths: list[Path] = []

    for item in plugins_raw:
        if not isinstance(item, dict):
            continue
        for plugin_name in item:
            template_path = settings.PLUGINS_DIR / f"{plugin_name}.jinja2"
            if not template_path.exists():
                raise FileNotFoundError(
                    f"Template plugin non trovato: \"{template_path}\""
                )
            if template_path not in seen:
                seen.add(template_path)
                paths.append(template_path)

    return paths


def load(input_file: Path) -> dict | None:
    input_file = Path(input_file)
    if not (input_file.exists() and input_file.is_file()):
        raise FileNotFoundError(f"File non trovato: \"{input_file}\"")

    plugin_paths: list[Path] = []
    if input_file.suffix.lower() in (".md", ".markdown"):
        plugin_paths = _estrai_plugin_paths(input_file)

    dati = None
    checksum_origine = _calcola_sha1(input_file, plugin_paths or None)
    file_cache = settings.CACHE_DIR / (checksum_origine + ".pickle")
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
    Carica un file frontmatter con YAML + Markdown.

    Se nel frontmatter sono dichiarati plugin, sostituisce i
    placeholder {{< nome >}} con l'HTML renderizzato prima di
    convertire il markdown in HTML. Il campo "content_raw"
    conserva sempre il markdown originale con i placeholder.

    Args:
        input_file: Path del file markdown da caricare.

    Returns:
        Dict con le chiavi del frontmatter più "content_raw"
        (markdown originale) e "content" (HTML finale).
    """

    data = frontmatter.load(input_file)
    temp = {}
    if data.metadata:
        temp |= _normalize_keys(data.metadata)

    content_raw = data.content or ""
    temp["content_raw"] = content_raw

    plugins_raw = data.metadata.get("plugins") or []
    if plugins_raw:
        content_raw = _renderizza_plugin(content_raw, plugins_raw)

    temp["content"] = markdown.markdown(content_raw)

    return temp

def clean():
    """
    Ripulisce la cartella di cache,
    Cancellando tutti i file non utilizzati
    durante l'esecuzione
    """

    # Rimuove tutti i file con estensione
    # .pickle che non sono stati utilizzati
    for file_cache in settings.CACHE_DIR.glob("*.pickle"):
        if file_cache.name not in _used_cache_files:
            try:
                file_cache.unlink()
            except Exception:
                pass
    
    # Rimuove eventuali file con estensione
    # .tmp rimasti orfani
    for tmp in settings.CACHE_DIR.glob("*.tmp"):
        try:
            tmp.unlink()
        except Exception:
            pass


# Inizializzazione
# Giusto per essere certi che CACHE_DIR esista
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)