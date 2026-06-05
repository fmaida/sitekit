import os
import sys
import time
from pathlib import Path

import pytest

import sitekit.cache as cache_module
from sitekit.cache import clean, load
from sitekit.cache import ram
from sitekit.settings import settings


# ---------------------------------------------------------------------------
# Costanti per i file di test
# ---------------------------------------------------------------------------

_MD_SEMPLICE = """\
---
title: Pagina di test
autore: Francesco
---

# Titolo

Contenuto di prova.
"""

_MD_CON_PLUGIN = """\
---
title: Pagina con plugin
plugins:
    - galleria:
          sorgente: "images/test"
---

# Titolo

{{< galleria >}}
"""

_MD_DUE_PLUGIN = """\
---
title: Pagina con due gallerie
plugins:
    - galleria:
          sorgente: "images/prima"
    - galleria:
          sorgente: "images/seconda"
---

Prima: {{< galleria >}}

Seconda: {{< galleria >}}
"""

_MD_PLUGIN_MANCANTE = """\
---
title: Plugin inesistente
plugins:
    - fantasma:
          param: "valore"
---

{{< fantasma >}}
"""

_TEMPLATE_GALLERIA = '<div class="galleria" data-src="{{ sorgente }}"></div>'

_TEMPLATE_GALLERIA_V2 = '<section class="gallery" data-path="{{ sorgente }}"></section>'


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
def md_semplice(tmp_path: Path) -> Path:
    p = tmp_path / "pagina.md"
    p.write_text(_MD_SEMPLICE, encoding="utf-8")

    return p


@pytest.fixture
def template_galleria() -> Path:
    p = settings.PLUGINS_DIR / "galleria.jinja2"
    p.write_text(_TEMPLATE_GALLERIA, encoding="utf-8")

    return p


@pytest.fixture
def md_con_plugin(tmp_path: Path) -> Path:
    p = tmp_path / "con_plugin.md"
    p.write_text(_MD_CON_PLUGIN, encoding="utf-8")

    return p


@pytest.fixture
def md_due_plugin(tmp_path: Path) -> Path:
    p = tmp_path / "due_plugin.md"
    p.write_text(_MD_DUE_PLUGIN, encoding="utf-8")

    return p


def _pickle_count() -> int:
    """Conta i file .pickle nella CACHE_DIR corrente."""

    return len(list(settings.CACHE_DIR.glob("*.pickle")))


def _reset_runtime_cache() -> None:
    """Azzera RAM e set dei file usati senza toccare i pickle su disco."""

    ram.CACHE.clear()
    ram.memoria_occupata = 0
    cache_module._used_cache_files.clear()


# ---------------------------------------------------------------------------
# Test: caricamento base senza plugin
# ---------------------------------------------------------------------------

class TestCaricamentoBase:

    def test_restituisce_dict(self, md_semplice: Path) -> None:
        dati = load(md_semplice)

        assert isinstance(dati, dict)


    def test_chiavi_frontmatter_presenti(self, md_semplice: Path) -> None:
        dati = load(md_semplice)

        assert dati["title"] == "Pagina di test"
        assert dati["autore"] == "Francesco"


    def test_content_raw_e_content_presenti(self, md_semplice: Path) -> None:
        dati = load(md_semplice)

        assert "content_raw" in dati
        assert "content" in dati


    def test_content_e_html(self, md_semplice: Path) -> None:
        dati = load(md_semplice)

        assert "<h1>" in dati["content"]
        assert "<p>" in dati["content"]


    def test_content_raw_e_markdown_grezzo(self, md_semplice: Path) -> None:
        dati = load(md_semplice)

        assert "# Titolo" in dati["content_raw"]
        assert "<h1>" not in dati["content_raw"]


    def test_pickle_creato_su_disco(self, md_semplice: Path) -> None:
        load(md_semplice)

        assert _pickle_count() == 1


    def test_file_non_trovato_solleva_eccezione(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load(tmp_path / "non_esiste.md")


# ---------------------------------------------------------------------------
# Test: cache hit (disco e RAM)
# ---------------------------------------------------------------------------

class TestCacheHit:

    def test_due_chiamate_restituiscono_dati_identici(
        self, md_semplice: Path
    ) -> None:
        dati1 = load(md_semplice)
        dati2 = load(md_semplice)

        assert dati1 == dati2


    def test_due_chiamate_non_creano_pickle_duplicati(
        self, md_semplice: Path
    ) -> None:
        load(md_semplice)
        load(md_semplice)

        assert _pickle_count() == 1


    def test_hit_da_disco_dopo_reset_ram(self, md_semplice: Path) -> None:
        load(md_semplice)
        ram.CACHE.clear()
        ram.memoria_occupata = 0

        dati = load(md_semplice)

        assert dati["title"] == "Pagina di test"
        assert _pickle_count() == 1


# ---------------------------------------------------------------------------
# Test: invalidazione cache su file modificato
# ---------------------------------------------------------------------------

class TestInvalidazioneSuFileModificato:

    def test_contenuto_aggiornato_dopo_modifica(
        self, md_semplice: Path
    ) -> None:
        load(md_semplice)
        _reset_runtime_cache()

        md_semplice.write_text(
            _MD_SEMPLICE.replace("Contenuto di prova.", "Testo aggiornato."),
            encoding="utf-8",
        )
        dati = load(md_semplice)

        assert "Testo aggiornato." in dati["content_raw"]


    def test_modifica_crea_nuovo_pickle(self, md_semplice: Path) -> None:
        load(md_semplice)
        _reset_runtime_cache()

        md_semplice.write_text(
            _MD_SEMPLICE.replace("Contenuto di prova.", "Testo aggiornato."),
            encoding="utf-8",
        )
        load(md_semplice)

        assert _pickle_count() == 2


    def test_clean_rimuove_pickle_obsoleto(self, md_semplice: Path) -> None:
        load(md_semplice)
        _reset_runtime_cache()

        md_semplice.write_text(
            _MD_SEMPLICE.replace("Contenuto di prova.", "Testo aggiornato."),
            encoding="utf-8",
        )
        load(md_semplice)
        clean()

        assert _pickle_count() == 1


# ---------------------------------------------------------------------------
# Test: plugin / shortcode
# ---------------------------------------------------------------------------

class TestPlugin:

    def test_placeholder_sostituito_nel_content(
        self, md_con_plugin: Path, template_galleria: Path
    ) -> None:
        dati = load(md_con_plugin)

        assert "{{< galleria >}}" not in dati["content"]
        assert 'data-src="images/test"' in dati["content"]


    def test_placeholder_conservato_in_content_raw(
        self, md_con_plugin: Path, template_galleria: Path
    ) -> None:
        dati = load(md_con_plugin)

        assert "{{< galleria >}}" in dati["content_raw"]


    def test_template_mancante_solleva_filenotfounderror(
        self, tmp_path: Path
    ) -> None:
        md = tmp_path / "mancante.md"
        md.write_text(_MD_PLUGIN_MANCANTE, encoding="utf-8")

        with pytest.raises(FileNotFoundError):
            load(md)


    def test_jinja2_mancante_solleva_importerror(
        self,
        md_con_plugin: Path,
        template_galleria: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setitem(sys.modules, "jinja2", None)

        with pytest.raises(ImportError):
            load(md_con_plugin)


    def test_matching_posizionale_due_plugin_stesso_tipo(
        self, md_due_plugin: Path, template_galleria: Path
    ) -> None:
        dati = load(md_due_plugin)
        content = dati["content"]

        pos_prima = content.index('data-src="images/prima"')
        pos_seconda = content.index('data-src="images/seconda"')

        assert pos_prima < pos_seconda


# ---------------------------------------------------------------------------
# Test: invalidazione cache su template modificato
# ---------------------------------------------------------------------------

class TestInvalidazioneSuTemplateModificato:

    @staticmethod
    def _modifica_template(template: Path, nuovo_contenuto: str) -> None:
        """
        Scrive nuovo contenuto nel template e forza un mtime
        in nanosecondi garantito diverso dall'originale,
        indipendentemente dalla velocità del filesystem.
        """

        mtime_originale_ns = template.stat().st_mtime_ns
        template.write_text(nuovo_contenuto, encoding="utf-8")
        os.utime(
            template,
            ns=(
                template.stat().st_atime_ns,
                mtime_originale_ns + 1_000_000_000,
            ),
        )


    def test_modifica_template_restituisce_html_aggiornato(
        self, md_con_plugin: Path, template_galleria: Path
    ) -> None:
        dati1 = load(md_con_plugin)
        _reset_runtime_cache()

        self._modifica_template(template_galleria, _TEMPLATE_GALLERIA_V2)
        dati2 = load(md_con_plugin)

        assert dati1["content"] != dati2["content"]
        assert "<section" in dati2["content"]


    def test_modifica_template_crea_nuovo_pickle(
        self, md_con_plugin: Path, template_galleria: Path
    ) -> None:
        load(md_con_plugin)
        _reset_runtime_cache()

        self._modifica_template(template_galleria, _TEMPLATE_GALLERIA_V2)
        load(md_con_plugin)

        assert _pickle_count() == 2


    def test_clean_dopo_modifica_template_rimuove_pickle_obsoleto(
        self, md_con_plugin: Path, template_galleria: Path
    ) -> None:
        load(md_con_plugin)
        _reset_runtime_cache()

        self._modifica_template(template_galleria, _TEMPLATE_GALLERIA_V2)
        load(md_con_plugin)
        clean()

        assert _pickle_count() == 1
