from datetime import date
from pathlib import Path

import pytest
from PIL import Image

import sitekit.cache as cache_module
from sitekit import assets, pagebundle
from sitekit.cache import ram
from sitekit.images import imgcache
from sitekit.images import images as images_module
from sitekit.pagebundle.nomi import _analizza_nome
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
    Isola ogni test: sposta su tmp_path le cartelle della cache, dei
    plugin e della pipeline degli asset, e azzera i globali di modulo
    che sopravvivrebbero da un test all'altro.
    """

    cache_dir = tmp_path / ".cache"
    cache_dir.mkdir()
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    monkeypatch.setattr(settings, "CACHE_DIR", cache_dir)
    monkeypatch.setattr(settings, "PLUGINS_DIR", plugins_dir)
    monkeypatch.setattr(settings, "RESOURCES_DIR", tmp_path / "resources")
    monkeypatch.setattr(settings, "STATIC_DIR", tmp_path / "static")
    monkeypatch.setattr(settings, "ASSETS_DIR", tmp_path / "assets")
    monkeypatch.setattr(settings, "ASSETS_URL", "/assets")

    ram.CACHE.clear()
    ram.memoria_occupata = 0
    cache_module._used_cache_files.clear()

    imgcache.CACHE = set()
    images_module.ultima_immagine = None
    images_module.ultima_immagine_sha1 = None


@pytest.fixture
def immagine(tmp_path: Path):
    """
    Genera un JPEG sintetico dentro una cartella, come fa
    tests/test_images.py.
    """

    def _crea(cartella: Path, nome: str = "foto.jpg") -> Path:
        percorso = cartella / nome
        Image.new("RGB", (200, 150), color=(100, 150, 200)).save(percorso, "JPEG")

        return percorso

    return _crea


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
    unito = pagebundle.load(ESEMPI / "esempio_unito")
    separato = pagebundle.load(ESEMPI / "esempio_separato")

    assert _senza_slug(unito) == _senza_slug(separato)


def test_cartelle_lingua_equivalgono_al_suffisso():
    separato = pagebundle.load(ESEMPI / "esempio_separato")
    cartelle = pagebundle.load(ESEMPI / "esempio_cartelle_lingua")

    assert _senza_slug(separato) == _senza_slug(cartelle)


def test_esempio_reale_ha_le_sezioni_attese():
    dati = pagebundle.load(ESEMPI / "esempio_separato")

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
    dati = pagebundle.load(bundle)

    assert dati["title"] == "Titolo"
    assert dati["subsection"]["title"] == "Titolo della sottosezione"


def test_load_su_file_esplicito(bundle: Path):
    dati = pagebundle.load(bundle / "index.md")

    assert dati["subsection"]["title"] == "Titolo della sottosezione"


def test_load_su_cartella_senza_indice(tmp_path: Path):
    vuota = tmp_path / "vuota"
    vuota.mkdir()

    with pytest.raises(FileNotFoundError, match="Index not found"):
        pagebundle.load(vuota)


def test_load_su_percorso_inesistente(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        pagebundle.load(tmp_path / "fantasma")


def test_bundle_con_underscore_index(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "_index.md").write_text(_INDICE, encoding="utf-8")
    (cartella / "_index.subsection.md").write_text(_SEZIONE, encoding="utf-8")

    dati = pagebundle.load(cartella)

    assert dati["subsection"]["title"] == "Titolo della sottosezione"


def test_sottocartella_non_lingua_viene_ignorata(bundle: Path):
    figlia = bundle / "figlia"
    figlia.mkdir()
    (figlia / "index.md").write_text(
        "---\ntitle: Pagina figlia\n---\n", encoding="utf-8"
    )

    dati = pagebundle.load(bundle)

    assert dati["title"] == "Titolo"


# ---------------------------------------------------------------------------
# Slug
# ---------------------------------------------------------------------------

def test_slug_dal_nome_cartella(bundle: Path):
    assert pagebundle.load(bundle)["slug"] == "pagina"


def test_slug_vuoto_nella_root_dei_contenuti(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "CONTENT_DIR", tmp_path)
    (tmp_path / "index.md").write_text(_INDICE, encoding="utf-8")

    assert pagebundle.load(tmp_path)["slug"] == ""


def test_slug_dal_frontmatter_vince(bundle: Path):
    (bundle / "index.md").write_text(
        "---\ntitle: Titolo\nslug: personalizzato\n---\n", encoding="utf-8"
    )

    assert pagebundle.load(bundle)["slug"] == "personalizzato"


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def test_file_di_sezione_vince_sul_frontmatter_inline(bundle: Path):
    dati = pagebundle.load(bundle)

    assert dati["subsection"]["title"] == "Titolo della sottosezione"


def test_sezione_annidata(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "index.history.gallery.md").write_text(
        "---\ntitle: Galleria\n---\n", encoding="utf-8"
    )

    dati = pagebundle.load(cartella)

    assert dati["history"]["gallery"]["title"] == "Galleria"


def test_sezione_con_frontmatter_a_sequenza(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "index.gallery.md").write_text(
        "---\n- item: uno\n- item: due\n---\n", encoding="utf-8"
    )

    dati = pagebundle.load(cartella)

    assert dati["gallery"] == [{"item": "uno"}, {"item": "due"}]


def test_sequenza_con_corpo_e_errore(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "index.gallery.md").write_text(
        "---\n- item: uno\n---\n\nCorpo di troppo\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="frontmatter a sequenza"):
        pagebundle.load(cartella)


def test_sequenza_come_indice_e_errore(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\n- item: uno\n---\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="frontmatter a sequenza"):
        pagebundle.load(cartella)


# ---------------------------------------------------------------------------
# Contenuti
# ---------------------------------------------------------------------------

def test_content_e_content_raw_a_ogni_livello(bundle: Path):
    dati = pagebundle.load(bundle)

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

    dati = pagebundle.load(cartella)

    assert dati["intro"]["content_raw"] == "Testo in **grassetto**"
    assert dati["intro"]["content"] == "<p>Testo in <strong>grassetto</strong></p>"


def test_content_vuoto_non_lascia_chiavi(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "index.intro.md").write_text(
        "---\ntitle: Intro\n---\n", encoding="utf-8"
    )

    dati = pagebundle.load(cartella)

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

    dati = pagebundle.load(cartella)

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

    dati = pagebundle.load(cartella)

    assert dati["title"] == "Titolo"
    assert dati["localization"]["en"]["title"] == "Title"


def test_sezione_presente_solo_in_una_lingua(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text("---\ntitle: Titolo\n---\n", encoding="utf-8")
    (cartella / "index.extra.en.md").write_text(
        "---\ntitle: Extra\n---\n", encoding="utf-8"
    )

    dati = pagebundle.load(cartella)

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

    inglese = pagebundle.load(cartella)["localization"]["en"]

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
        pagebundle.load(cartella)


def test_localizzato_fa_fallback_sulla_lingua_di_default():
    dati = pagebundle.load(ESEMPI / "esempio_separato")
    inglese = pagebundle.localizzato(dati, "en")

    assert inglese["intro"]["title"] == "Authentic flavours, Venetian tradition"
    assert inglese["cuisine"]["title"] == "Il menù"
    assert "localization" not in inglese


def test_localizzato_con_lingua_sconosciuta():
    dati = pagebundle.load(ESEMPI / "esempio_separato")
    tedesco = pagebundle.localizzato(dati, "de")

    assert tedesco["intro"]["title"] == "Sapori autentici, tradizione veneziana"


# ---------------------------------------------------------------------------
# Asset relativi
# ---------------------------------------------------------------------------

def test_immagine_diventa_un_tag_picture(tmp_path: Path, immagine):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    immagine(cartella)
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n![Una bella foto](foto.jpg)\n", encoding="utf-8"
    )

    html = pagebundle.load(cartella)["content"]

    assert "<picture>" in html
    assert 'alt="Una bella foto"' in html
    assert '/assets/images/pagina/foto/foto__800.jpg' in html
    assert '/assets/images/pagina/foto/foto__400.avif' in html


def test_i_file_puntati_dal_picture_esistono(tmp_path: Path, immagine):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    immagine(cartella)
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n![](foto.jpg)\n", encoding="utf-8"
    )

    pagebundle.load(cartella)
    assets.build()

    generata = settings.ASSETS_DIR / "images" / "pagina" / "foto" / "foto__800.jpg"

    assert generata.is_file()


def test_link_a_immagine_punta_al_breakpoint_grande(tmp_path: Path, immagine):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    immagine(cartella)
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n[grande](foto.jpg)\n", encoding="utf-8"
    )

    html = pagebundle.load(cartella)["content"]

    assert 'href="/assets/images/pagina/foto/foto__1600.jpg"' in html


def test_file_generico_copiato_tal_quale(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "doc.pdf").write_bytes(b"%PDF-1.4 finto")
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n[scarica](doc.pdf)\n", encoding="utf-8"
    )

    dati = pagebundle.load(cartella)

    assert 'href="/assets/images/pagina/doc.pdf"' in dati["content"]
    assert (
        settings.CACHE_DIR / "assets" / "images" / "pagina" / "doc.pdf"
    ).is_file()


def test_asset_relativo_da_cartella_lingua(tmp_path: Path, immagine):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    immagine(cartella)
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    (cartella / "en").mkdir()
    (cartella / "en" / "index.md").write_text(
        "---\ntitle: T\n---\n\n[Una bella foto](foto.jpg)\n", encoding="utf-8"
    )

    inglese = pagebundle.load(cartella)["localization"]["en"]

    assert 'href="/assets/images/pagina/foto/foto__1600.jpg"' in inglese["content"]


def test_riferimento_a_file_inesistente_resta_invariato(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n[niente](fantasma.pdf)\n", encoding="utf-8"
    )

    assert 'href="fantasma.pdf"' in pagebundle.load(cartella)["content"]


def test_asset_in_sottocartella_resta_invariato(tmp_path: Path):
    """
    media.copia guarda solo la root del bundle: riscrivere un
    riferimento a una sottocartella darebbe un URL verso un file che
    nessuno ha copiato.
    """

    cartella = tmp_path / "pagina"
    (cartella / "video").mkdir(parents=True)
    (cartella / "video" / "clip.mp4").write_bytes(b"finto")
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n[guarda](video/clip.mp4)\n", encoding="utf-8"
    )

    assert 'href="video/clip.mp4"' in pagebundle.load(cartella)["content"]


def test_file_di_contenuto_non_diventa_un_asset(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "dati.yaml").write_text("chiave: valore\n", encoding="utf-8")
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n[dati](dati.yaml)\n", encoding="utf-8"
    )

    dati = pagebundle.load(cartella)

    assert 'href="dati.yaml"' in dati["content"]
    assert not (
        settings.CACHE_DIR / "assets" / "images" / "pagina" / "dati.yaml"
    ).exists()


def test_copia_asset_disattivata_non_tocca_il_disco(tmp_path: Path, immagine):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    immagine(cartella)
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n![](foto.jpg)\n", encoding="utf-8"
    )

    dati = pagebundle.load(cartella, copia_asset=False)

    assert 'src="foto.jpg"' in dati["content"]
    assert not (settings.CACHE_DIR / "assets").exists()


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

    html = pagebundle.load(cartella)["content"]

    assert 'href="https://example.com/x.jpg"' in html
    assert 'href="/menu/"' in html
    assert 'href="#storia"' in html
    assert 'href="mailto:info@example.com"' in html


def test_content_raw_non_viene_riscritto(tmp_path: Path, immagine):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    immagine(cartella)
    (cartella / "index.md").write_text(
        "---\ntitle: T\n---\n\n![](foto.jpg)\n", encoding="utf-8"
    )

    assert pagebundle.load(cartella)["content_raw"] == "![](foto.jpg)"


def test_frontmatter_non_viene_riscritto(tmp_path: Path):
    cartella = tmp_path / "pagina"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\nimage: WSW_1826\n---\n", encoding="utf-8"
    )

    assert pagebundle.load(cartella)["image"] == "WSW_1826"


def test_senza_bundle_gli_asset_restano_relativi(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "CONTENT_DIR", tmp_path)
    (tmp_path / "index.md").write_text(
        "---\ntitle: T\n---\n\n![](foto.jpg)\n", encoding="utf-8"
    )

    assert 'src="foto.jpg"' in pagebundle.load(tmp_path)["content"]


# ---------------------------------------------------------------------------
# date, cover e collezioni
# ---------------------------------------------------------------------------

def test_date_normalizzata_a_iso(tmp_path: Path):
    cartella = tmp_path / "post"
    cartella.mkdir()
    (cartella / "index.md").write_text(
        "---\ntitle: T\ndate: 2026-03-07\n---\n", encoding="utf-8"
    )

    assert pagebundle.load(cartella)["date"] == "2026-03-07"


def test_date_assente_resta_assente(bundle: Path):
    assert "date" not in pagebundle.load(bundle)


def test_cover_dal_nome_file(tmp_path: Path, immagine):
    cartella = tmp_path / "post"
    cartella.mkdir()
    immagine(cartella, "scatto_cover.jpg")
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")

    assert pagebundle.load(cartella)["cover"] == "scatto_cover"


def test_senza_cover_nessuna_chiave(tmp_path: Path, immagine):
    cartella = tmp_path / "post"
    cartella.mkdir()
    immagine(cartella)
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")

    assert "cover" not in pagebundle.load(cartella)


def test_load_collection_ordina_per_data(tmp_path: Path):
    blog = tmp_path / "blog"
    for nome, giorno in (("secondo", "2026-02-01"), ("primo", "2026-01-01")):
        cartella = blog / nome
        cartella.mkdir(parents=True)
        (cartella / "index.md").write_text(
            f"---\ntitle: {nome}\ndate: {giorno}\n---\n", encoding="utf-8"
        )

    posts = pagebundle.load_collection(blog)

    assert [p["slug"] for p in posts] == ["primo", "secondo"]


def test_load_collection_riempie_le_date_mancanti(tmp_path: Path):
    blog = tmp_path / "blog"
    cartella = blog / "senza-data"
    cartella.mkdir(parents=True)
    (cartella / "index.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")

    posts = pagebundle.load_collection(blog)

    assert posts[0]["date"] == date.today().strftime("%Y-%m-%d")


def test_load_single_e_un_alias_di_load():
    assert pagebundle.load_single is pagebundle.load


# ---------------------------------------------------------------------------
# Regressione router
# ---------------------------------------------------------------------------

def test_router_non_scambia_una_sezione_per_una_lingua(tmp_path: Path):
    router = Router(cartella_base=tmp_path)

    with pytest.raises(ValueError, match="convenzione"):
        router.verso_url(tmp_path / "chi-siamo" / "index.intro.md")
