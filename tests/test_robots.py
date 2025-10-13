import shutil

import pytest
from sitekit import robots
from sitekit.settings import settings

@pytest.fixture(autouse=True, scope="module")
def inizializza():
    if settings.BUILD_DIR.exists():
        shutil.rmtree(settings.BUILD_DIR)

def test_creazione_robots_txt_senza_sitemap():
    if settings.BUILD_DIR.exists():
        (settings.BUILD_DIR / "sitemap.xml").unlink(exists_ok=True)
    robots.generate()
    robots_txt = (settings.BUILD_DIR / "robots.txt").read_text()

    assert (settings.BUILD_DIR / "robots.txt").exists()
    assert "Sitemap:" not in robots_txt

def test_creazione_robots_txt_con_sitemap():
    sitemap = settings.BUILD_DIR / "sitemap.xml"
    sitemap.touch()
    robots.generate()

    robots_txt = (settings.BUILD_DIR / "robots.txt").read_text()

    assert (settings.BUILD_DIR / "robots.txt").exists()
    assert robots_txt.startswith("User-agent: *\n")
    assert f"Sitemap: {settings.BASE_URL}/sitemap.xml" in robots_txt