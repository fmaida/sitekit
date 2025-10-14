from pathlib import Path


class PictureClass:

    CODICE = """
    <picture>
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
    </picture>
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
    
    def __str__(self):
        base = str(self._tronca_a_static(self.folder))
        return PictureClass.CODICE.strip().format(base=base)