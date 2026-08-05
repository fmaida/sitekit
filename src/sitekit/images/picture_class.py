from pathlib import Path


class PictureClass:

    CODICE = """<picture>
    <source type="image/avif" srcset="
        {base}/{stem}__400.avif 400w,
        {base}/{stem}__800.avif 800w,
        {base}/{stem}__1200.avif 1200w,
        {base}/{stem}__1600.avif 1600w
    " sizes="(max-width: 800px) 100vw, 800px">
    <source type="image/webp" srcset="
        {base}/{stem}__400.webp 400w,
        {base}/{stem}__800.webp 800w,
        {base}/{stem}__1200.webp 1200w,
        {base}/{stem}__1600.webp 1600w
    " sizes="(max-width: 800px) 100vw, 800px">
    <img src="{base}/{stem}__800.jpg" srcset="
        {base}/{stem}__400.jpg 400w,
        {base}/{stem}__800.jpg 800w,
        {base}/{stem}__1200.jpg 1200w,
        {base}/{stem}__1600.jpg 1600w
    " sizes="(max-width: 800px) 100vw, 800px" alt="{alt}" loading="lazy">
</picture>"""

    def __init__(self, folder: Path, alt: str = "", base_url: str | None = None):
        """
        Args:
            folder: cartella su disco che contiene i breakpoint
                generati, il cui nome è lo stem dell'immagine
                sorgente.
            alt: testo alternativo per il tag <img>.
            base_url: URL pubblico della cartella. Va passato da chi
                conosce la pipeline degli asset (di norma
                `assets.url(...)`); se manca, l'URL viene dedotto dal
                percorso su disco, che funziona solo finché i file
                stanno sotto una cartella chiamata "static".
        """

        self.folder = folder
        self.alt = alt
        self.base_url = base_url

    @staticmethod
    def _tronca_a_static(path: Path) -> str:
        path_str = str(path)
        idx = path_str.find("/static")
        if idx != -1:
            return path_str[idx:]
        return path_str

    def __str__(self):
        if self.base_url is not None:
            base = self.base_url.rstrip("/")
        else:
            base = str(self._tronca_a_static(self.folder))
        stem = self.folder.name
        return PictureClass.CODICE.format(base=base, stem=stem, alt=self.alt)
