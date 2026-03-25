"""
Test di integrazione sul feed reale: tests/examples/rss/memos_rss_01.xml

Item 0  "Sweet Fightin' +2"   — enclosure image/jpeg  → image presente
Item 1  "Drill Dozer"         — enclosure image/gif   → image presente
Item 6  "SuperSprite"         — enclosure video/mp4   → image=None
Item 11 "Star Dust Wars"      — nessun enclosure      → image=None

feedparser.parse() accetta direttamente il contenuto XML come stringa,
quindi i test non richiedono rete.
"""
import pytest
import feedparser
from pathlib import Path

from sitekit import rssreader
from sitekit.rssreader import memos

EXAMPLES_DIR = Path(__file__).parent / "examples" / "rss"


@pytest.fixture(scope="module")
def feed_memos():
    """
    Legge da disco il file tests/examples/rss/memos_rss_01.xml
    """

    xml = (EXAMPLES_DIR / "memos_rss_01.xml").read_text(encoding="utf-8")
    return feedparser.parse(xml)


# ─── Struttura del feed ───────────────────────────────────────────────────────

def test_feed_ha_almeno_sei_item(feed_memos):
    assert len(feed_memos.entries) >= 6


# ─── memos.importa sul feed reale ─────────────────────────────────────────────

def test_primo_item_title_non_vuoto_e_senza_html(feed_memos):
    risultato = memos.importa(feed_memos.entries[0])
    assert risultato["title"]
    assert "<" not in risultato["title"]
    assert ">" not in risultato["title"]

def test_primo_item_url(feed_memos):
    assert feed_memos.entries[0].link == "https://cesco.blog/memos/cdAffFzYTYgpDPk49bP4tT"

def test_primo_item_body_non_vuoto_e_senza_html(feed_memos):
    risultato = memos.importa(feed_memos.entries[0])
    assert risultato["body"]
    assert "<" not in risultato["body"]
    assert ">" not in risultato["body"]

def test_immagine_da_enclosure_jpeg(feed_memos):
    """Item 0: enclosure image/jpeg → image è l'URL del file .jpg."""
    risultato = memos.importa(feed_memos.entries[0])
    assert risultato["image"] == (
        "https://cesco.blog/file/attachments/"
        "REoeKqbgLsUbtg567wGqGe/sf2-zx-spectrum-T8EaKi.jpg"
    )

def test_immagine_da_enclosure_gif(feed_memos):
    """Item 1 (Drill Dozer): enclosure image/gif → image presente."""
    risultato = memos.importa(feed_memos.entries[1])
    assert risultato["image"] is not None
    assert risultato["image"].endswith(".gif")

def test_enclosure_video_ignorato(feed_memos):
    """Item 6 (SuperSprite): enclosure video/mp4 → image deve essere None."""
    risultato = memos.importa(feed_memos.entries[6])
    assert risultato["image"] is None

def test_nessun_enclosure(feed_memos):
    """Item 11 (Star Dust Wars): nessun enclosure → image deve essere None."""
    risultato = memos.importa(feed_memos.entries[11])
    assert risultato["image"] is None


# ─── load() sul feed reale ────────────────────────────────────────────────────

def test_load_struttura_completa(feed_memos, monkeypatch):
    """load() restituisce sempre le quattro chiavi su dati reali."""
    monkeypatch.setattr(feedparser, "parse", lambda url: feed_memos)
    result = rssreader.load("https://cesco.blog/explore/rss.xml", source="memos", limit=3)
    assert len(result) == 3
    for articolo in result:
        assert set(articolo.keys()) == {"title", "url", "image", "body"}

def test_load_campi_testuali_senza_html(feed_memos, monkeypatch):
    """title e body non contengono tag HTML su dati reali."""
    monkeypatch.setattr(feedparser, "parse", lambda url: feed_memos)
    result = rssreader.load("https://cesco.blog/explore/rss.xml", source="memos", limit=3)
    for articolo in result:
        assert "<" not in articolo["title"]
        assert "<" not in articolo["body"]

def test_load_url_assoluti(feed_memos, monkeypatch):
    """Tutti gli url nell'output sono URL assoluti."""
    monkeypatch.setattr(feedparser, "parse", lambda url: feed_memos)
    result = rssreader.load("https://cesco.blog/explore/rss.xml", source="memos", limit=3)
    for articolo in result:
        assert articolo["url"].startswith("https://")
