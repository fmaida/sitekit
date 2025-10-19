import yaml
from pathlib import Path
from .classes import OpeningsClass
from sitekit.settings import settings


def load(config_file: Path) -> OpeningsClass:
    config = {}
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        with open(settings.CONTENT_DIR / config_file, "r") as f:
            config = yaml.safe_load(f)
    return OpeningsClass(config_text=config)