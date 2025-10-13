from sitekit.settings import CONTENT_DIR, STATIC_DIR
from pathlib import Path
from . import images, imgcache
from .classes import PictureClass


def copy(source_image: Path, destination_folder: Path, aspect_ratio="unchanged") -> PictureClass:
    """
    Copia un immagine salvandola in varie dimensioni

    Args:
        source_image: Percorso all'immagine originale
        destination_folder: Percorso alla cartella destinazione
        aspect_ratio: Aspect ratio da mantenere nella conversione

    Returns:
        un istanza di PictureClass contenente tutte
        le informazioni i dati per gestire l'immagine
    """

    # Controlla che quello in input sia un file
    # esistente
    if not source_image.exists() or not source_image.is_file():
        raise FileNotFoundError(
            f"Non è un immagine valida: {str(source_image)}"
        )
        
    # Verifica che la cartella di output esista        
    destination_folder /= source_image.stem
    destination_folder.mkdir(parents=True, exist_ok=True)

    try:
        s = images.copy_single(source_image, destination_folder, 
                    longest_side=400, aspect_ratio="unchanged")
        s = images.copy_single(source_image, destination_folder, 
                    longest_side=800, aspect_ratio="unchanged")
        s = images.copy_single(source_image, destination_folder, 
                    longest_side=1200, aspect_ratio="unchanged")
        s = images.copy_single(source_image, destination_folder, 
                    longest_side=1600, aspect_ratio="unchanged")        
    except Exception as e:
         print(f"Errore durante la copia: {e}")

    return PictureClass(folder=destination_folder)