from pathlib import Path
from flask import url_for


class PictureClass:

    CODICE = """    
    <source type="image/avif" srcset="
        {base}/immagine__400.avif 400w,
        {base}/immagine__800.avif 800w,
        {base}/immagine__1200.avif 1200w,
        {base}/immagine__1600.avif 1600w
    " sizes="(max-width: 800px) 100vw, 800px">
    <source type="image/webp" srcset="
        {base}/immagine__400.webp 400w,
        {base}/immagine__800.webp 800w,
        {base}/immagine__1200.webp 1200w,
        {base}/immagine__1600.webp 1600w
    " sizes="(max-width: 800px) 100vw, 800px">
    <img src="{base}/immagine__800.jpg" srcset="
        {base}/immagine__400.jpg 400w,
        {base}/immagine__800.jpg 800w,
        {base}/immagine__1200.jpg 1200w,
        {base}/immagine__1600.jpg 1600w
    " sizes="(max-width: 800px) 100vw, 800px" alt="Descrizione immagine" loading="lazy">    
    """
    
    def __init__(self, folder: Path):
        self.folder = folder

    @staticmethod
    def _tronca_a_static(path: Path) -> str:
        path_str = str(path)
        idx = path_str.find("/static")
        if idx != -1:
            return path_str[idx:]

        return path_str

    def format(self, image_format: str, image_size: int) -> str:
        base = str(self._tronca_a_static(self.folder))
        base += "/immagine__{image_size}.{image_format}"
        base = url_for("static", filename=base)
        return f"{base}"

    def render(self, css_class: str = "") -> str:
        base = str(self._tronca_a_static(self.folder))
        base = url_for("static", filename=base)
        if self.css_class != "":
            beginning = f'<picture class="{self.css_class}">'
        else:
            beginning = "<picture>"
        ending = "</picture>"
        return beginning + PictureClass.CODICE.strip().format(base=base) + ending

    def __str__(self):
        return self.render()


class PictureListClass:

    def __init__(self):
        self.pictures = []

    def append(self, picture: PictureClass):
        self.pictures.append(picture)

    def sort(self):
        """
        Riordina le immagini trovate mettendo quelle
        che contengono la sottostringa `_cover`
        in alto. Così abbiamo sempre l'immagine di
        copertina come prima immagine

        Returns:
            None
        """
        self.pictures.sort(key=lambda p: (0 if "_cover" in p.folder.stem else 1, p.folder.stem.lower()))

    def __list__(self):
        return self.pictures