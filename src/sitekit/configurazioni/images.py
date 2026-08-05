from PIL import Image
from pathlib import Path
import os
import hashlib
import io
import logging
import shutil
from sitekit.assets import percorsi
from sitekit.settings import settings
from .imgcache import cache_aggiungi


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache_conversioni = {}

# Helper checksum SHA1 del file su disco
def _sha1_of_file(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def image_copier(folder_name: Path, image_path: Path):
    """
    Preleva un'immagine selezionata dalla cartella `places/<folder_name>`
    la converte nei formati .avif, .webp e .jpg riducendone le dimensioni, 
    ed infine la salva nella cartella `static/images/<folder_name>`.

    args:
        folder_name (Path): Contiene il nome della cartella da cui viene
                            prelevata l'immagine (es: "scla")
        image_path (Path): È il percorso assoluto al file immagine nella
                            cartella "content"

    returns:
        str: Il nome del file indicato da <folder_name> senza estensione.
    """

    #logger.info(f"Avvio della copia immagine")        
    
    # Preleva il nome del file senza estensione
    # (mi servirà più tardi) e prepara l'URL
    # alla cartella destinazione da cui saranno
    # accessibili le immagini convertite
    image_name = image_path.stem
    output_path = f"/static/images/{folder_name}/{image_name}"

    # Verifica se ha già effettuato il lavoro di
    # conversione per quest'immagine
    unchanged = cache_aggiungi(image_path)
    if unchanged:
        if VERBOSE:
            logger.info(f"L'immagine esiste già. La salto.")
        return output_path

    # Ottiene la cartella di output delle
    # immagini dentro la cartella build
    build_images_dir = settings.BUILD_DIR / "assets" / "images" / folder_name

    # Crea la cartella e le precedenti se non esistono
    build_images_dir.mkdir(parents = True, exist_ok=True)

    # Ottiene la cartella di output delle immagini
    # generate, dentro la cache: da lì assets.build()
    # le porta nella cartella servita
    static_images_dir = percorsi.destinazione(f"images/{folder_name}")

    if VERBOSE:
        logger.info("--------------------------------")
        logger.info(f"Inizio la conversione dell'immagine \"{image_path}\"")

    # Se non lo ha mai fatto prima, 
    # allora possiamo procedere!    

    # Apri l'immagine con Pillow
    # Ottieni il nome del file senza estensione    
    with Image.open(image_path) as img:
    
        # Converti in RGB se ha canale alpha
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGB")

        # Ridimensiona l'immagine a massimo 1200 pixel
        # nel lato più lungo,mantenendo il 
        # rapporto d'aspetto
        max_size = 1200
        width, height = img.size
        if max(width, height) > max_size:
            # L'immagine in almeno uno dei lati 
            # è più lunga del consentito
            if width >= height:
                # Se è orizzontale la riscala
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                # Se è verticale la riscala
                new_height = max_size
                new_width = int(width * (max_size / height))
            # Riscala l'immagine in memoria
            img = img.resize((new_width, new_height), Image.LANCZOS)

        # Percorsi di output per la cartella src/static
        static_avif_path = static_images_dir / (image_name + ".avif")
        static_webp_path = static_images_dir / (image_name + ".webp")
        static_jpg_path = static_images_dir / (image_name + ".jpg")
        
        # Percorsi di output per la cartella build
        build_avif_path = build_images_dir / (image_name + ".avif")
        build_webp_path = build_images_dir / (image_name + ".webp")
        build_jpg_path = build_images_dir / (image_name + ".jpg")        

        if VERBOSE:
            logger.info("Procedo a convertire l'immagine")
        
        # 1) Calcola checksum del JPEG esistente (se presente)
        old_jpg_sha1 = _sha1_of_file(static_jpg_path)

        # 2) Prepara un JPEG in memoria (più veloce, senza I/O su disco)
        jpg_buffer = io.BytesIO()
        img.save(jpg_buffer, format="JPEG", quality=70)
        jpg_bytes = jpg_buffer.getvalue()

        # 3) Calcola checksum del JPEG in memoria
        new_jpg_sha1 = hashlib.sha1(jpg_bytes).hexdigest()

        # 4) Se non sono identici, scrivi il JPEG su disco e crea anche AVIF e WEBP
        #    altrimenti salta tutte le ricompressioni (il JPEG su disco è già identico)
        if old_jpg_sha1 != new_jpg_sha1:
            # Scrivi il JPEG solo se è stato
            # cambiato

            # Prima nella cartella static
            with open(static_jpg_path, "wb") as f:
                f.write(jpg_bytes)

            # E poi nella cartella build
            with open(build_jpg_path, "wb") as f:
                f.write(jpg_bytes)                

            # Salva in formato .avif
            static_avif_path.unlink(missing_ok=True)
            build_avif_path.unlink(missing_ok=True)
            try:
                img.save(static_avif_path, format="AVIF", quality=70, method=6)
            except Exception as e:
                logger.warning(f"AVIF static fallito: {e}")
            try:
                img.save(build_avif_path, format="AVIF", quality=70, method=6)
            except Exception as e:
                logger.warning(f"AVIF build fallito: {e}")

            # Salva in formato .webp
            static_webp_path.unlink(missing_ok=True)
            build_webp_path.unlink(missing_ok=True)
            try:
                img.save(static_webp_path, format="WEBP", quality=70, method=6)
            except Exception as e:
                logger.warning(f"WEBP static fallito: {e}")
            try:
                img.save(build_webp_path, format="WEBP", quality=70, method=6)
            except Exception as e:
                logger.warning(f"WEBP build fallito: {e}")

        for src, dst in [
            (static_jpg_path,  build_jpg_path),
            (static_webp_path, build_webp_path),
            (static_avif_path, build_avif_path),
        ]:
            if os.path.exists(src) and not os.path.exists(dst):
                try:
                    shutil.copy2(src, dst)
                    if VERBOSE:
                        logger.info(f"Copiato in build (post): {dst}")
                except Exception as e:
                    logger.warning(f"Copia in build (post) fallita per {dst}: {e}")

    # Restituisce il nome del file indicato da <folder_name> senza estensione
    return output_path

def marca_come_convertite(folder_name):
    """
    Marca la cartella come convertita, così non la converte più
    durante la sessione di lavoro attuale.
    """
    cache_conversioni[folder_name] = True
    return f"/static/images/{folder_name}/"