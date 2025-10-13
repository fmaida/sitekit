#from .configurazioni.images import image_copier
from . import configurazioni 
from .localize import localizza_stringhe
from .configurazioni.themes import _carica_temi
from .configurazioni.imgcache import (cache_salva, 
                    cache_svuota, CACHE)
from .configurazioni import descrizioni
from .settings import (BASE_DIR,
                       BASE_URL,
                       CACHE_DIR,
                       CONTENT_DIR,
                       LOCALE_DIR,
                       BUILD_DIR,
                       STATIC_DIR,
                       TEMPLATES_DIR,
                       SITE_LANGUAGES,
                       SITE_LANGUAGE_CODES,
                       SITE_LANGUAGE_NAMES)