from typing import Tuple
from pathlib import Path
import os
import hashlib
import io
import logging
import shutil

from PIL import Image, ImageOps
from sitekit.settings import settings
from . import imgcache

def copy_single(input_file: Path, output_folder_path: Path, longest_side: int = 1200, output_formats: list = None, aspect_ratio="unchanged", anchor: str = "middle") -> bool:
    """
    Copies and processes an image from the input path to the output folder, resizing and converting it to specified formats.

    This function takes an input image and applies a series of transformations while ensuring efficient reuse of previously processed or cached image data.
    The transformations include optional cropping to a specified aspect ratio, resizing the longest side, and exporting the image in multiple output formats.
    The function supports formats including AVIF, WebP, and JPEG. Output images are stored in the specified output directory.

    Arguments:
        input_file (Path):
            The path to the input image file.
        output_folder_path (Path):
            The directory where processed images
            will be stored.
        longest_side (int, optional):
            Maximum allowed size for the longest
            side of the image. Default is 1200 pixels.
        output_formats (list, optional):
            List of desired output formats. Supported
            values are "avif", "webp", and "jpeg".
            Defaults to ["avif", "webp", "jpeg"].
        aspect_ratio (str, optional):
            Specifies whether to crop the image to a
            given aspect ratio. Defaults to "unchanged".
        anchor (str, optional):
            Vertical crop anchor when the image is taller than the target ratio.
            One of "top", "middle", or "bottom". Defaults to "middle".

    Returns:
        bool:
            True if the operation is successful and
            at least one image is saved, False otherwise.

    Raises:
        ValueError:
            If an unsupported format is specified in the output_formats list,
            or if `anchor` is not one of "top", "middle", "bottom".
    """
    global ultima_immagine
    global ultima_immagine_sha1

    if output_formats is None:
        output_formats = ["avif", "webp", "jpeg"]

    # verifica_e_aggiungi calcola lo SHA-1 e lo restituisce per evitare
    # di ricalcolarlo qui sotto nella gestione della cache RAM
    da_elaborare, hash_calcolato = imgcache.verifica_e_aggiungi(
        input_file, longest_side, output_folder_path, aspect_ratio, anchor)

    if not da_elaborare:
        return False

    # Per evitare di caricare il file continuamente da disco,
    # tiene in RAM una copia dell'ultima immagine aperta.
    # hash_calcolato proviene già da imgcache: nessun doppio calcolo.
    if ultima_immagine:
        if ultima_immagine_sha1 == hash_calcolato:
            # È lo stesso file: riusa l'immagine già in memoria
            pass
        else:
            # File diverso: chiude il precedente e apre il nuovo
            ultima_immagine.close()
            ultima_immagine = Image.open(input_file)
            ultima_immagine_sha1 = hash_calcolato
    else:
        # Prima immagine: carica e memorizza subito anche lo SHA-1
        ultima_immagine = Image.open(input_file)
        ultima_immagine_sha1 = hash_calcolato

    # Copia la variabile per valore, non per
    # riferimento. Questo è MOLTO importante,
    # per evitare di modificare la variabile
    # in modo irreparabile, visto che poi
    # mi servirà in altre occasioni
    img = ultima_immagine.copy()

    # Controlla l'orientamento EXIF
    img = ImageOps.exif_transpose(img)

    # Apri l'immagine con Pillow
    # Ottieni il nome del file senza estensione

    # Crop (opzionale)
    if aspect_ratio.lower() != "unchanged":
        box = _crop_box(img.size, aspect_ratio, anchor)
        if box != (0, 0, img.size[0], img.size[1]):
            img = img.crop(box)

    # Riscala l'immagine, se necessario
    width, height = img.size
    if max(width, height) > longest_side:
        # L'immagine in almeno uno dei lati
        # è più lunga del consentito
        if width >= height:
            # Se è orizzontale la riscala
            new_width = longest_side
            new_height = int(height * (longest_side / width))
        else:
            # Se è verticale la riscala
            new_height = longest_side
            new_width = int(width * (longest_side / height))
        # Riscala l'immagine in memoria
        img = img.resize((new_width, new_height), Image.LANCZOS)

    output_folder_path.mkdir(parents=True, exist_ok=True)
    nome_file = input_file.stem + "__" + str(longest_side)
    percorso_file = output_folder_path / nome_file

    # Salva le immagini sul disco
    for fmt in output_formats:
        fmt_l = fmt.lower()
        if fmt_l in ("jpeg", "jpg"):
            im_save = img.convert("RGB") if img.mode != "RGB" else img
            outp = (output_folder_path / nome_file).with_suffix(".jpg")
            im_save.save(outp, "JPEG", quality=75, optimize=True, progressive=True)
        elif fmt_l == "webp":
            outp = (output_folder_path / nome_file).with_suffix(".webp")
            img.save(outp, "WEBP", quality=82, method=6)
        elif fmt_l == "avif":
            outp = (output_folder_path / nome_file).with_suffix(".avif")
            # richiede pillow-avif-plugin
            img.save(outp, "AVIF", quality=50, speed=6)
        else:
            raise ValueError(f"Formato non supportato: {fmt}")

    return True

def _crop_box(wh: Tuple[int, int], aspect: str, anchor: str = "middle") -> Tuple[int, int, int, int]:
    if aspect == "unchanged":
        return (0, 0, wh[0], wh[1])

    w, h = wh

    # Validate anchor (vertical only: top/middle/bottom)
    anchor_l = anchor.lower()
    if anchor_l not in ("top", "middle", "bottom"):
        raise ValueError(f"Anchor non valido: {anchor}. Valori ammessi: 'top', 'middle', 'bottom'.")

    # Parse aspect ratio "W:H"
    num, den = aspect.split(":")
    ar = float(num) / float(den)

    cur = w / h

    if cur > ar:
        # Image is wider than target: crop left/right, keep vertical centered
        new_w = int(h * ar)
        if new_w >= w:
            return (0, 0, w, h)
        left = (w - new_w) // 2
        return (left, 0, left + new_w, h)
    else:
        # Image is taller than target: crop top/middle/bottom
        new_h = int(w / ar)
        if new_h >= h:
            return (0, 0, w, h)
        if anchor_l == "top":
            top = 0
        elif anchor_l == "bottom":
            top = h - new_h
        else:  # middle (center)
            top = (h - new_h) // 2
        return (0, top, w, top + new_h)


# Inizializzazione
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache_conversioni = {}

# Cerca di ricordarsi l'ultima immagine
# su cui ha lavorato
ultima_immagine = None
ultima_immagine_sha1 = None