#from .configurazioni.images import image_copier
from . import configurazioni 
from .localize import localizza_stringhe
from .configurazioni.themes import _carica_temi
from .configurazioni.imgcache import (cache_salva, 
                    cache_svuota, CACHE)
from .configurazioni import descrizioni
from .shortcuts import content, i18n
from . import assets
from . import pagebundle
from .settings import settings