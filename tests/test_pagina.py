from pathlib import Path

import pytest

import sitekit.cache as cache_module
from sitekit import pagina
from sitekit.cache import ram
from sitekit.pagina.nomi import _analizza_nome
from sitekit.router import Router
from sitekit.settings import settings


ESEMPI = Path(__file__).parent / "examples" / "frontmatter+markdown"


# ---------------------------------------------------------------------------
# Costanti per i file di test
# ---------------------------------------------------------------------------

_INDICE = """\
---
title: Titolo
subsection:
    title: Titolo inline
---

Questo è il contenuto principale
"""

_SEZIONE = """\
---
title: Titolo della sottosezione
---

Questo è il contenuto della sottosezione
"""

_TEMPLATE_GALLERIA = '<div class="galleria" data-src="{{ sorgente }}"></div>'


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Isola ogni test: reindirizza CACHE_DIR e PLUGINS_DIR su tmp_path
    e azzera la RAM cache e il set dei file usati.
    """

    cache_dir = tmp_path / ".cache"
    cache_dir.mkdir()
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    monkeypatch.setattr(settings, "CACHE_DIR", cache_dir)
    monkeypatch.setattr(settings, "PLUGINS_DIR", plugins_dir)

    ram.CACHE.clear()
    ram.memoria_occupata = 0
    cache_module._used_cache_files.clear()


@pytest.fixture
def bundle(tmp_path: Path) -> Path:
    """
    Page bundle minimo con indice e una sottosezione.
    """

    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(_INDICE, encoding="utf-8")
    (cartella / "index.subsection.md").write_text(_SEZIONE, encoding="utf-8")

    return cartella


def _senza_slug(dati: dict) -> dict:
    """
    Copia il dizionario senza lo slug, che dipende dal nome cartella.
    """

    return {c: v for c, v in dati.items() if c != "slug"}


# ---------------------------------------------------------------------------
# Identità tra le forme
# ---------------------------------------------------------------------------

def test_unito_e_separato_producono_lo_stesso_dizionario():
    unito = pagina.load(ESEMPI / "esempio_unito")
    separato = pagina.load(ESEMPI / "esempio_separato")

    assert _senza_slug(unito) == _senza_slug(separato)


def test_cartelle_lingua_equivalgono_al_suffisso():
    separato = pagina.load(ESEMPI / "esempio_separato")
    cartelle = pagina.load(ESEMPI / "esempio_cartelle_lingua")

    assert _senza_slug(separato) == _senza_slug(cartelle)


def test_esempio_reale_ha_le_sezioni_attese():
    dati = pagina.load(ESEMPI / "esempio_separato")

    assert dati["title"] == "Trattoria Alla Scala"
    assert dati["intro"]["pretitle"] == "La nostra filosofia"
    assert dati["history"]["gallery"][0]["item"] == "WSW_1801"
    assert "<strong>Trattoria Alla Scala</strong>" in dati["history"]["content"]


# ---------------------------------------------------------------------------
# Parsing dei nomi file
# ---------------------------------------------------------------------------

def test_nome_indice_non_ha_segmenti():
    assert _analizza_nome("index.md", "index") == ([], "it")


def test_nome_con_sezione():
    assert _analizza_nome("index.intro.md", "index") == (["intro"], "it")


def test_nome_con_sezione_annidata():
    segmenti, lingua = _analizza_nome("index.history.gallery.md", "index")

    assert segmenti == ["history", "gallery"]
    assert lingua == "it"


def test_nome_con_lingua():
    assert _analizza_nome("index.intro.en.md", "index") == (["intro"], "en")


def test_lingua_dalla_cartella():
    assert _analizza_nome("index.intro.md", "index", "en") == (["intro"], "en")


def test_suffisso_lingua_dentro_cartella_lingua_e_errore():
    with pytest.raises(ValueError, match="cartella-lingua"):
        _analizza_nome("index.intro.fr.md", "index", "en")


def test_segmento_di_un_carattere_e_errore():
    with pytest.raises(ValueError, match="troppo corto"):
        _analizza_nome("index.a.md", "index")


def test_lingua_non_finale_e_errore():
    # "en" non è in coda, quindi resta un segmento di sezione troppo corto
    with pytest.raises(ValueError, match="troppo corto"):
        _analizza_nome("index.en.intro.md", "index")


def test_stem_diverso_e_errore():
    with pytest.raises(ValueError, match="non appartiene"):
        _analizza_nome("altro.intro.md", "index")


# ---------------------------------------------------------------------------
# Page bundle
# ---------------------------------------------------------------------------

def test_load_su_cartella_trova_index(bundle: Path):
    dati = pagina.load(bundle)

    assert dati["title"] == "Titolo"
    assert dati["subsection"]["title"] == "Titolo della sottosezione"


def test_load_su_file_esplicito(bundle: Path):
    dati = pagina.load(bundle / "index.md")

    assert dati["subsection"]["title"] == "Titolo della sottosezione"


def test_load_su_cartella_senza_indice(tmp_path: Path):
    vuota = tmp_path / "vuota"
    vuota.mkdir()

    with pytest.raises(FileNotFoundError, match="Index not found"):
        pagina.load(vuota)


def test_load_su_percorso_inesistente(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        pagina.load(tmp_path / "fantasma")


def test_bundle_con_underscore_index(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "_index.md").write_text(_INDICE, encoding="utf-8")
    (cartella / "_index.subsection.md").write_text(_SEZIONE, encoding="utf-8")

    dati = pagina.load(cartella)

    assert dati["subsection"]["title"] == "Titolo della sottosezione"


def test_sottocartella_non_lingua_viene_ignorata(bundle: Path):
    figlia = bundle / "figlia"
    figlia.mkdir()
    (figlia / "index.md").write_text(
        "---\ntitle: Pagina figlia\n---\n", encoding="utf-8"
    )

    dati = pagina.load(bundle)

    assert dati["title"] == "Titolo"


# ---------------------------------------------------------------------------
# Slug
# ---------------------------------------------------------------------------

def test_slug_dal_nome_cartella(bundle: Path):
    assert pagina.load(bundle)["slug"] == "pagina"


def test_slug_vuoto_nella_root_dei_contenuti(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "CONTENT_DIR", tmp_path)
    (tmp_path / "index.md").write_text(_INDICE, encoding="utf-8")

    assert pagina.load(tmp_path)["slug"] == ""


def test_slug_dal_frontmatter_vince(bundle: Path):
    (bundle / "index.md").write_text(
        "---\ntitle: Titolo\nslug: personalizzato\n---\n", encoding="utf-8"
    )

    assert pagina.load(bundle)["slug"] == "personalizzato"


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def test_file_di_sezione_vince_sul_frontmatter_inline(bundle: Path):
    dati = pagina.load(bundle)

    assert dati["subsection"]["title"] == "Titolo della sottosezione"


def test_sezione_annidata(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "index.history.gallery.md").write_text(
        "---\ntitle: Galleria\n---\n", encoding="utf-8"
    )

    dati = pagina.load(cartella)

    assert dati["history"]["gallery"]["title"] == "Galleria"


def test_sezione_con_frontmatter_a_sequenza(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "index.gallery.md").write_text(
        "---\n- item: uno\n- item: due\n---\n", encoding="utf-8"
    )

    dati = pagina.load(cartella)

    assert dati["gallery"] == [{"item": "uno"}, {"item": "due"}]


def test_sequenza_con_corpo_e_errore(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "index.gallery.md").write_text(
        "---\n- item: uno\n---\n\nCorpo di troppo\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="frontmatter a sequenza"):
        pagina.load(cartella)


def test_sequenza_come_indice_e_errore(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\n- item: uno\n---\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="frontmatter a sequenza"):
        pagina.load(cartella)


# ---------------------------------------------------------------------------
# Contenuti
# ---------------------------------------------------------------------------

def test_content_e_content_raw_a_ogni_livello(bundle: Path):
    dati = pagina.load(bundle)

    assert dati["content_raw"] == "Questo è il contenuto principale"
    assert dati["content"] == "<p>Questo è il contenuto principale</p>"
    assert dati["subsection"]["content"] == (
        "<p>Questo è il contenuto della sottosezione</p>"
    )


def test_content_inline_viene_renderizzato(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\nintro:\n  content: Testo in **grassetto**\n---\n",
        encoding="utf-8",
    )

    dati = pagina.load(cartella)

    assert dati["intro"]["content_raw"] == "Testo in **grassetto**"
    assert dati["intro"]["content"] == "<p>Testo in <strong>grassetto</strong></p>"


def test_content_vuoto_non_lascia_chiavi(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "index.intro.md").write_text(
        "---\ntitle: Intro\n---\n", encoding="utf-8"
    )

    dati = pagina.load(cartella)

    assert "content" not in dati["intro"]
    assert "content_raw" not in dati["intro"]


def test_shortcode_dentro_un_file_di_sezione(tmp_path: Path):
    (settings.PLUGINS_DIR / "galleria.jinja2").write_text(
        _TEMPLATE_GALLERIA, encoding="utf-8"
    )

    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "index.intro.md").write_text(
        '---\ntitle: Intro\n---\n\n{{< galleria sorgente="images/test" />}}\n',
        encoding="utf-8",
    )

    dati = pagina.load(cartella)

    # data-src non è un riferimento a un asset del bundle: il template
    # lo risolve per conto suo e non va riscritto.
    assert 'data-src="images/test"' in dati["intro"]["content"]


# ---------------------------------------------------------------------------
# Localizzazione
# ---------------------------------------------------------------------------

def test_localization_raccoglie_le_lingue_non_default(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: Titolo\n---\n", encoding="utf-8")
    (cartella / "index.en.md").write_text("---\ntitle: Title\n---\n", encoding="utf-8")

    dati = pagina.load(cartella)

    assert dati["title"] == "Titolo"
    assert dati["localization"]["en"]["title"] == "Title"


def test_sezione_presente_solo_in_una_lingua(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: Titolo\n---\n", encoding="utf-8")
    (cartella / "index.extra.en.md").write_text(
        "---\ntitle: Extra\n---\n", encoding="utf-8"
    )

    dati = pagina.load(cartella)

    assert "extra" not in dati
    assert dati["localization"]["en"]["extra"]["title"] == "Extra"


def test_cartella_lingua_vince_sul_file_suffissato(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: Titolo\n---\n", encoding="utf-8")
    (cartella / "index.en.md").write_text(
        "---\ntitle: Dal suffisso\nextra: presente\n---\n", encoding="utf-8"
    )
    (cartella / "en").mkdir()
    (cartella / "en" / "index.md").write_text(
        "---\ntitle: Dalla cartella\n---\n", encoding="utf-8"
    )

    inglese = pagina.load(cartella)["localization"]["en"]

    assert inglese["title"] == "Dalla cartella"
    assert inglese["extra"] == "presente"


def test_suffisso_lingua_dentro_cartella_lingua_solleva(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: Titolo\n---\n", encoding="utf-8")
    (cartella / "en").mkdir()
    (cartella / "en" / "index.fr.md").write_text(
        "---\ntitle: Titre\n---\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="cartella-lingua"):
        pagina.load(cartella)


def test_localizzato_fa_fallback_sulla_lingua_di_default():
    dati = pagina.load(ESEMPI / "esempio_separato")
    inglese = pagina.localizzato(dati, "en")

    assert inglese["intro"]["title"] == "Authentic flavours, Venetian tradition"
    assert inglese["cuisine"]["title"] == "Il menù"
    assert "localization" not in inglese


def test_localizzato_con_lingua_sconosciuta():
    dati = pagina.load(ESEMPI / "esempio_separato")
    tedesco = pagina.localizzato(dati, "de")

    assert tedesco["intro"]["title"] == "Sapori autentici, tradizione veneziana"


# ---------------------------------------------------------------------------
# Asset relativi
# ---------------------------------------------------------------------------

def test_asset_relativo_ancorato_alla_root_del_bundle(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n![](foto.jpg)\n", encoding="utf-8"
    )

    dati = pagina.load(cartella)

    assert 'src="/static/cache/pagina/foto.jpg"' in dati["content"]


def test_asset_relativo_da_cartella_lingua(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "en").mkdir()
    (cartella / "en" / "index.md").write_text(
        "---\ntitle: T\n---\n\n[Una bella foto](foto.jpg)\n", encoding="utf-8"
    )

    inglese = pagina.load(cartella)["localization"]["en"]

    assert 'href="/static/cache/pagina/foto.jpg"' in inglese["content"]


def test_asset_gia_assoluti_restano_invariati(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n"
        "[esterno](https://example.com/x.jpg)\n\n"
        "[radice](/menu/)\n\n"
        "[ancora](#storia)\n\n"
        "[mail](mailto:info@example.com)\n",
        encoding="utf-8",
    )

    html = pagina.load(cartella)["content"]

    assert 'href="https://example.com/x.jpg"' in html
    assert 'href="/menu/"' in html
    assert 'href="#storia"' in html
    assert 'href="mailto:info@example.com"' in html


def test_content_raw_non_viene_riscritto(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n![](foto.jpg)\n", encoding="utf-8"
    )

    assert pagina.load(cartella)["content_raw"] == "![](foto.jpg)"


def test_frontmatter_non_viene_riscritto(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\nimage: WSW_1826\n---\n", encoding="utf-8"
    )

    assert pagina.load(cartella)["image"] == "WSW_1826"


def test_senza_bundle_gli_asset_restano_relativi(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "CONTENT_DIR", tmp_path)
    (tmp_path / "index.md").write_text(
        "---\ntitle: T\n---\n\n![](foto.jpg)\n", encoding="utf-8"
    )

    assert 'src="foto.jpg"' in pagina.load(tmp_path)["content"]


# ---------------------------------------------------------------------------
# Regressione router
# ---------------------------------------------------------------------------

def test_router_non_scambia_una_sezione_per_una_lingua(tmp_path: Path):
    router = Router(cartella_base=tmp_path)

    with pytest.raises(ValueError, match="convenzione"):
        router.verso_url(tmp_path / "chi-siamo" / "index.intro.md")
