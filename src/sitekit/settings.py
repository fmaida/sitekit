from pathlib import Path
from babel import Locale


# Risali a partire dal file corrente 
# (__file__) fino a trovare pyproject.toml
def get_base_dir() -> Path:
    cur = Path(__file__).resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Non trovo la root del progetto (pyproject.toml mancante?)")

def carica_lingue_disponibili():
    """
    Carica le lingue tradotte disponibili.
    
    returns:
        list: Una lista di lingue disponibili.
    """
    lingue = []

    # Carica le lingue dal file locale    
    if LOCALE_DIR.exists() and LOCALE_DIR.is_dir():
        for file in LOCALE_DIR.iterdir():
            if file.is_file() and file.suffix == ".json":
                id_lingua = file.stem
                nome_lingua = Locale.parse(id_lingua).get_display_name()
                lingue.append((id_lingua, 
                               nome_lingua))

    # Ordina le lingue in ordine alfabetico in base al nome completo della lingua
    lingue.sort(key=lambda x: x[1])

    return lingue

# Parametri globali
BASE_DIR = get_base_dir()
BASE_URL = "https://venice.bio"
CACHE_DIR = BASE_DIR / ".cache"
CONTENT_DIR = BASE_DIR / "content"
BUILD_DIR = BASE_DIR / "build"
LOCALE_DIR = BASE_DIR / "locale"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
SITE_LANGUAGES = carica_lingue_disponibili()
SITE_LANGUAGE_CODES = [codice for codice, _ in SITE_LANGUAGES]
SITE_LANGUAGE_NAMES = [nome for _, nome in SITE_LANGUAGES]
VERBOSE = False