import pytest
import sitekit
from pathlib import Path


def test_impostazione_corretta_base_url():
    sitekit.settings.BASE_URL = "https://gigetto.com"

    assert sitekit.settings.BASE_URL == "https://gigetto.com"

def test_impostazione_corretta_base_dir():
    base_dir = Path(__file__).parent.parent

    assert sitekit.settings.BASE_DIR == base_dir

def test_impostazione_corretta_static_dir():
    static_dir = Path(__file__).parent.parent / "static"

    assert sitekit.settings.STATIC_DIR == static_dir

def test_impostazione_corretta_build_dir():
    build_dir = Path(__file__).parent.parent / "build"

    assert sitekit.settings.BUILD_DIR == build_dir

def test_impostazione_corretta_cache_dir():
    cache_dir = Path(__file__).parent.parent / ".cache"

    assert sitekit.settings.CACHE_DIR == cache_dir