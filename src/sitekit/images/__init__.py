# v1.1 – 29/09/2025

from sitekit.settings import settings
from pathlib import Path
from . import images, imgcache
from .picture_class import PictureClass


def copy(source_image: Path, destination_folder: Path, aspect_ratio: str = "unchanged", anchor: str = "middle", alt: str = "") -> PictureClass:
    """
    Copies an image file to a specified destination, creating multiple resized
    versions of the image with predefined sizes. Ensures the source file exists
    and the destination folder is created, if not already existent.

    Parameters:
        source_image (Path): The path of the image file to be copied.
        destination_folder (Path): The path of the folder where the image
            and its resized copies will be saved.
        aspect_ratio (str): The aspect ratio to maintain for the resized images.
            Default is "unchanged". Examples: "2:3", "4:3", "16:9", "9:16"
        anchor (str): The vertical anchor position for cropping the image.
        alt (str): Testo alternativo per il tag <img>. Importante per
            accessibilità e SEO. Default stringa vuota.

    Returns:
        PictureClass: An instance of PictureClass representing the folder
            containing the copied images.

    Raises:
        FileNotFoundError: If the source image file does not exist or is not
            a valid file.
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
                    longest_side=400, aspect_ratio=aspect_ratio, anchor=anchor)
        s = images.copy_single(source_image, destination_folder,
                    longest_side=800, aspect_ratio=aspect_ratio, anchor=anchor)
        s = images.copy_single(source_image, destination_folder, 
                    longest_side=1200, aspect_ratio=aspect_ratio, anchor=anchor)
        # L'ultimo è volutamente convertito con aspect ratio
        # non modificato rispetto all'originale: è il file che
        # spesso verrà usato per mostrare l'anteprima a tutto
        # schermo.
        s = images.copy_single(source_image, destination_folder,
                    longest_side=1600, aspect_ratio="unchanged", anchor=anchor)
    except Exception as e:
         print(f"Errore durante la copia: {e}")

    return PictureClass(folder=destination_folder, alt=alt)