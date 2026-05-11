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

    def __init__(self, folder: Path, alt: str = ""):
        self.folder = folder
        self.alt = alt

    @staticmethod
    def _tronca_a_static(path: Path) -> str:
        path_str = str(path)
        idx = path_str.find("/static")
        if idx != -1:
            return path_str[idx:]
        return path_str

    def __str__(self):
        base = str(self._tronca_a_static(self.folder))
        stem = self.folder.name
        return PictureClass.CODICE.format(base=base, stem=stem, alt=self.alt)
