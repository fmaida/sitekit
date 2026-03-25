import pytest
import feedparser
from types import SimpleNamespace
from unittest.mock import MagicMock

from sitekit import rssreader
from sitekit.rssreader._utils import strip_html
from sitekit.rssreader import memos, wordpress


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _mock_feed(entries):
    """Simula l'oggetto restituito da feedparser.parse()."""
    feed = MagicMock()
    feed.entries = entries
    return feed


def _entry_memos(**kwargs):
    """Crea una entry feedparser-like per Memos."""
    defaults = dict(
        title="",
        link="https://memos.example.com/m/123",
        summary="<p>Questo è un memo di prova.</p>",
        content=[],
        media_content=[],
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _entry_wp(**kwargs):
    """Crea una entry feedparser-like per WordPress."""
    defaults = dict(
        title="Titolo articolo",
        link="https://myblog.com/articolo",
        summary="<p>Riassunto breve.</p>",
        content=[],
        media_content=[],
        media_thumbnail=[],
        enclosures=[],
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ─── strip_html ───────────────────────────────────────────────────────────────

def test_strip_html_rimuove_tag():
    assert strip_html("<p>Ciao <b>mondo</b></p>") == "Ciao mondo"

def test_strip_html_decodifica_entita_html():
    assert strip_html("&lt;tag&gt; &amp; testo") == "<tag> & testo"

def test_strip_html_normalizza_spazi():
    assert strip_html("<p>Uno</p><p>Due</p>") == "Uno Due"

def test_strip_html_testo_vuoto():
    assert strip_html("") == ""

def test_strip_html_nessun_tag():
    assert strip_html("Testo senza tag") == "Testo senza tag"

def test_strip_html_nessun_tag_html_residuo():
    risultato = strip_html("<div><p>Testo <strong>in grassetto</strong></p></div>")
    assert "<" not in risultato
    assert ">" not in risultato


# ─── memos.importa ────────────────────────────────────────────────────────────

def test_memos_body_da_summary():
    entry = _entry_memos(summary="<p>Testo del memo</p>")
    result = memos.importa(entry)
    assert result["body"] == "Testo del memo"

def test_memos_body_da_content_se_presente():
    entry = _entry_memos(
        summary="<p>Riassunto</p>",
        content=[{"value": "<p>Testo completo del memo</p>"}],
    )
    result = memos.importa(entry)
    assert result["body"] == "Testo completo del memo"

def test_memos_body_senza_tag_html():
    entry = _entry_memos(summary="<p>Primo <b>paragrafo</b>.</p><p>Secondo.</p>")
    result = memos.importa(entry)
    assert "<" not in result["body"]
    assert ">" not in result["body"]

def test_memos_titolo_esplicito():
    entry = _entry_memos(title="Il mio titolo", summary="<p>Corpo</p>")
    result = memos.importa(entry)
    assert result["title"] == "Il mio titolo"

def test_memos_titolo_derivato_dal_body_se_assente():
    testo = "Uno due tre quattro cinque sei sette otto nove dieci"
    entry = _entry_memos(title="", summary=f"<p>{testo}</p>")
    result = memos.importa(entry)
    assert result["title"] != ""
    assert "…" in result["title"]

def test_memos_titolo_corto_senza_ellissi():
    entry = _entry_memos(title="", summary="<p>Tre parole sole</p>")
    result = memos.importa(entry)
    assert "…" not in result["title"]

def test_memos_titolo_senza_tag_html():
    entry = _entry_memos(title="<b>Titolo in grassetto</b>")
    result = memos.importa(entry)
    assert "<" not in result["title"]

def test_memos_immagine_da_media_content():
    entry = _entry_memos(
        media_content=[{"url": "https://example.com/img.jpg"}]
    )
    result = memos.importa(entry)
    assert result["image"] == "https://example.com/img.jpg"

def test_memos_immagine_da_img_nel_body():
    entry = _entry_memos(
        summary='<p><img src="https://example.com/foto.jpg" alt="foto"/> testo</p>'
    )
    result = memos.importa(entry)
    assert result["image"] == "https://example.com/foto.jpg"

def test_memos_immagine_none_se_assente():
    entry = _entry_memos(summary="<p>Nessuna immagine qui</p>")
    result = memos.importa(entry)
    assert result["image"] is None

def test_memos_media_content_ha_priorita_su_img_body():
    entry = _entry_memos(
        summary='<p><img src="https://example.com/inline.jpg"/></p>',
        media_content=[{"url": "https://example.com/cover.jpg"}],
    )
    result = memos.importa(entry)
    assert result["image"] == "https://example.com/cover.jpg"


# ─── wordpress.importa ────────────────────────────────────────────────────────

def test_wp_body_da_content():
    entry = _entry_wp(content=[{"value": "<p>Testo completo dell'articolo.</p>"}])
    result = wordpress.importa(entry)
    assert result["body"] == "Testo completo dell'articolo."

def test_wp_body_da_summary_se_content_assente():
    entry = _entry_wp(summary="<p>Solo il riassunto.</p>")
    result = wordpress.importa(entry)
    assert result["body"] == "Solo il riassunto."

def test_wp_body_senza_tag_html():
    entry = _entry_wp(summary="<p>Testo <em>enfatizzato</em>.</p>")
    result = wordpress.importa(entry)
    assert "<" not in result["body"]

def test_wp_immagine_da_media_content():
    entry = _entry_wp(media_content=[{"url": "https://myblog.com/cover.jpg"}])
    result = wordpress.importa(entry)
    assert result["image"] == "https://myblog.com/cover.jpg"

def test_wp_immagine_da_media_thumbnail():
    entry = _entry_wp(media_thumbnail=[{"url": "https://myblog.com/thumb.jpg"}])
    result = wordpress.importa(entry)
    assert result["image"] == "https://myblog.com/thumb.jpg"

def test_wp_immagine_da_enclosures():
    entry = _entry_wp(
        enclosures=[{"type": "image/jpeg", "href": "https://myblog.com/foto.jpg"}]
    )
    result = wordpress.importa(entry)
    assert result["image"] == "https://myblog.com/foto.jpg"

def test_wp_enclosure_non_immagine_ignorato():
    entry = _entry_wp(
        enclosures=[{"type": "audio/mpeg", "href": "https://myblog.com/audio.mp3"}]
    )
    result = wordpress.importa(entry)
    assert result["image"] is None

def test_wp_immagine_da_img_nel_body():
    entry = _entry_wp(
        summary='<img src="https://myblog.com/img.png"/> <p>testo</p>'
    )
    result = wordpress.importa(entry)
    assert result["image"] == "https://myblog.com/img.png"

def test_wp_media_content_ha_priorita_su_enclosure():
    entry = _entry_wp(
        media_content=[{"url": "https://myblog.com/cover.jpg"}],
        enclosures=[{"type": "image/jpeg", "href": "https://myblog.com/enc.jpg"}],
    )
    result = wordpress.importa(entry)
    assert result["image"] == "https://myblog.com/cover.jpg"

def test_wp_immagine_none_se_assente():
    entry = _entry_wp(summary="<p>Nessuna immagine.</p>")
    result = wordpress.importa(entry)
    assert result["image"] is None


# ─── load() ───────────────────────────────────────────────────────────────────

def test_load_source_non_supportato():
    with pytest.raises(ValueError, match="non supportato"):
        rssreader.load("https://example.com/feed.xml", source="sconosciuto")

def test_load_ritorna_lista(monkeypatch):
    entry = _entry_memos(title="Test", link="https://memos.example.com/m/1", summary="<p>Corpo</p>")
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed([entry]))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos")
    assert isinstance(result, list)
    assert len(result) == 1

def test_load_struttura_output(monkeypatch):
    entry = _entry_memos(title="Titolo", link="https://memos.example.com/m/1", summary="<p>Corpo</p>")
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed([entry]))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos")
    assert set(result[0].keys()) == {"title", "url", "image", "body"}

def test_load_limit(monkeypatch):
    entries = [_entry_memos(summary=f"<p>Memo {i}</p>") for i in range(20)]
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed(entries))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos", limit=4)
    assert len(result) == 4

def test_load_limit_default_sei(monkeypatch):
    entries = [_entry_memos(summary=f"<p>Memo {i}</p>") for i in range(20)]
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed(entries))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos")
    assert len(result) == 6

def test_load_url_articolo_presente(monkeypatch):
    entry = _entry_memos(link="https://memos.example.com/m/42", summary="<p>Memo</p>")
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed([entry]))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos")
    assert result[0]["url"] == "https://memos.example.com/m/42"

def test_load_testo_senza_html(monkeypatch):
    entry = _entry_memos(
        title="<b>Titolo</b>",
        summary="<p>Corpo <em>con</em> tag.</p>",
    )
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed([entry]))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos")
    assert "<" not in result[0]["title"]
    assert "<" not in result[0]["body"]

def test_load_body_troncato_a_500_caratteri(monkeypatch):
    entry = _entry_memos(summary=f"<p>{'a' * 600}</p>")
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed([entry]))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos")
    assert len(result[0]["body"]) <= 501  # 500 + "…"
    assert result[0]["body"].endswith("…")

def test_load_body_non_troncato_se_sotto_limite(monkeypatch):
    entry = _entry_memos(summary="<p>Ciao mondo</p>")
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed([entry]))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos")
    assert result[0]["body"] == "Ciao mondo"
    assert not result[0]["body"].endswith("…")

def test_load_body_limit_personalizzato(monkeypatch):
    entry = _entry_memos(summary=f"<p>{'parola ' * 50}</p>")
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed([entry]))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos", body_limit=100)
    assert len(result[0]["body"]) <= 101
    assert result[0]["body"].endswith("…")

def test_load_body_limit_zero_non_tronca(monkeypatch):
    entry = _entry_memos(summary=f"<p>{'x ' * 400}</p>")
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed([entry]))
    result = rssreader.load("https://memos.example.com/rss.xml", source="memos", body_limit=0)
    assert len(result[0]["body"]) > 500
    assert not result[0]["body"].endswith("…")

def test_load_output_sempre_quattro_chiavi_anche_con_connettore_incompleto(monkeypatch):
    """load() garantisce sempre title/url/image/body anche se il connettore
    restituisce chiavi mancanti o chiavi spurie non previste."""
    entry = _entry_memos(title="Test", link="https://example.com/m/1", summary="<p>x</p>")
    monkeypatch.setattr(feedparser, "parse", lambda url: _mock_feed([entry]))
    monkeypatch.setattr(
        "sitekit.rssreader._memos.importa",
        lambda entry: {"body": "testo", "chiave_spuria": "valore_extra"},
    )
    result = rssreader.load("https://example.com/rss.xml", source="memos")
    assert set(result[0].keys()) == {"title", "url", "image", "body"}
    assert "chiave_spuria" not in result[0]
