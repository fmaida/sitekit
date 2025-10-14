# v1.0 – 17/09/2025

from pathlib import Path
from datetime import datetime
import shutil
from sitekit import cache, images
from sitekit.settings import settings


MEDIA_DESTINATION_FOLDER = settings.STATIC_DIR / "cache"

def set_media_destination_folder(path: Path):
    global MEDIA_DESTINATION_FOLDER

    MEDIA_DESTINATION_FOLDER = path

def load_collection(path: Path):

    posts = []
    for item in path.glob("*"):
        if item.is_dir():
            posts.append(load_single(item))

    return sorted(posts, key=lambda x: x["date"])

def load_single(path: Path):
    data = None
    try:
        data = cache.load(path / "_index.md")
    except FileNotFoundError:
        try:
            data = cache.load(path / "index.md")
        except FileNotFoundError:
            raise FileNotFoundError(f"Index not found on \"{path}\".")

    cover_image = _copy_media(path)
    if cover_image:
        data["cover"] = cover_image
    data["slug"] = path.stem

    # Se non c'è una data come campo, la ricava dalla data di creazione del file
    if not data.get("date"):
        temp = path.stat().st_ctime
        temp2 = datetime.fromtimestamp(temp)
        data["date"] = temp2.strftime("%Y-%m-%d")
    else:
        try:
            data["date"] = data["date"].strftime("%Y-%m-%d")
        except AttributeError:
            pass
    return data

def _copy_media(path: Path):
    """
    Copia tutti i file multimediali nella cartella
    di destinazione. Se si tratta di immagini, le
    converte prima
    """
    global MEDIA_DESTINATION_FOLDER
    MEDIA_DESTINATION_FOLDER.mkdir(parents=True, exist_ok=True)

    cover_image = None
    image_types = [".jpg", ".jpeg", ".png"]
    ignore_types = [".md", ".yaml", ".yml", ".json"]

    destination = MEDIA_DESTINATION_FOLDER / path.stem
    destination.mkdir(exist_ok=True)

    for item in path.glob("*"):
        if item.is_file() and item.suffix.lower() in image_types:
            images.copy(source_image=item, destination_folder=destination, aspect_ratio="4:3")
            if "_cover" in item.stem:
                cover_image = item.stem
        elif item.is_file() and item.suffix.lower() not in ignore_types:
            shutil.copy2(item, destination)

    return cover_image