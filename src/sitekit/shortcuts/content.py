from pathlib import Path

from sitekit import cache
from sitekit.settings import settings


def load(input_file: Path) -> dict | None:
    return cache.load(settings.CONTENT_DIR / input_file)