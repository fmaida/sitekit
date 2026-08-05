"""
Pipeline degli asset: dai sorgenti alla cartella servita.

    resources/           sorgenti DA ELABORARE (immagini da ridimensionare)
    static/              sorgenti GIÀ PRONTI (css, js, font)
    content/<bundle>/    immagini dei page bundle, accanto al markdown
            │
            │  conversione (images.copy)
            ▼
    .cache/assets/       output delle conversioni
            │
            │  assets.build()
            ▼
    assets/              unica cartella servita in dev e copiata nel build

`resources/` e `static/` sono le uniche cartelle che si modificano a
mano; `assets/` e `.cache/` sono generate e vanno in .gitignore.
"""

from .costruzione import build, register
from .percorsi import cartella_generati, destinazione, url

__all__ = [
    "build",
    "cartella_generati",
    "destinazione",
    "register",
    "url",
]
