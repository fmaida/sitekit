import sys
from pathlib import Path

import pytest

from sitekit import shortcodes
from sitekit.shortcodes.attributi import analizza_attributi
from sitekit.shortcodes.processore import ProcessoreShortcode
from sitekit.settings import settings


# ---------------------------------------------------------------------------
# Template di test
# ---------------------------------------------------------------------------

_TEMPLATE_FIGURE = (
    '<figure><img src="{{ url }}" alt="{{ alt | default(\'\') }}">'
    "{% if content %}<figcaption>{{ content }}</figcaption>{% endif %}"
    "</figure>"
)

_TEMPLATE_NOTA = '<aside class="{{ tipo | default(\'info\') }}">{{ content | safe }}</aside>'


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def plugins_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Reindirizza PLUGINS_DIR su una cartella temporanea con i
    template di test.
    """

    cartella = tmp_path / "plugins"
    cartella.mkdir()
    (cartella / "figure.jinja2").write_text(_TEMPLATE_FIGURE, encoding="utf-8")
    (cartella / "nota.jinja2").write_text(_TEMPLATE_NOTA, encoding="utf-8")

    monkeypatch.setattr(settings, "PLUGINS_DIR", cartella)

    return cartella


# ---------------------------------------------------------------------------
# Test: parser degli attributi
# ---------------------------------------------------------------------------

class TestAnalizzaAttributi:

    def test_doppi_apici(self) -> None:
        attributi = analizza_attributi(' url="/img.jpg" alt="Gigetto" ')

        assert attributi == {"url": "/img.jpg", "alt": "Gigetto"}


    def test_singoli_apici(self) -> None:
        attributi = analizza_attributi(" tipo='avviso' ")

        assert attributi == {"tipo": "avviso"}


    def test_stringa_vuota(self) -> None:
        assert analizza_attributi("") == {}


    def test_nome_con_trattino(self) -> None:
        attributi = analizza_attributi(' data-src="x" ')

        assert attributi == {"data-src": "x"}


# ---------------------------------------------------------------------------
# Test: shortcode {{< >}} (contenuto grezzo)
# ---------------------------------------------------------------------------

class TestAngolo:

    def test_autochiuso_con_attributi(self) -> None:
        html = shortcodes.renderizza('{{< figure url="/a.jpg" alt="A" />}}')

        assert '<img src="/a.jpg" alt="A">' in html
        assert "<figcaption>" not in html


    def test_autochiuso_senza_spazio(self) -> None:
        html = shortcodes.renderizza('{{< figure url="/a.jpg"/>}}')

        assert '<img src="/a.jpg"' in html


    def test_accoppiato_passa_il_contenuto(self) -> None:
        sorgente = '{{< figure url="/a.jpg" >}}Una **didascalia**{{< end >}}'
        html = shortcodes.renderizza(sorgente)

        assert "<figcaption>Una **didascalia**</figcaption>" in html


    def test_contenuto_grezzo_non_convertito(self) -> None:
        sorgente = "{{< figure url=\"/a.jpg\" >}}**no markdown**{{< end >}}"
        html = shortcodes.renderizza(sorgente)

        assert "<strong>" not in html


# ---------------------------------------------------------------------------
# Test: shortcode {{% %}} (contenuto Markdown)
# ---------------------------------------------------------------------------

class TestPercento:

    def test_contenuto_convertito_da_markdown(self) -> None:
        sorgente = "{{% nota tipo=\"warning\" %}}Ciao a **tutti**{{% end %}}"
        html = shortcodes.renderizza(sorgente)

        assert "<strong>tutti</strong>" in html
        assert 'class="warning"' in html


    def test_tipo_di_default(self) -> None:
        html = shortcodes.renderizza("{{% nota %}}testo{{% end %}}")

        assert 'class="info"' in html


    def test_autochiuso(self) -> None:
        html = shortcodes.renderizza('{{% nota tipo="warning" /%}}')

        assert 'class="warning"' in html


# ---------------------------------------------------------------------------
# Test: convivenza auto-chiusi e accoppiati
# ---------------------------------------------------------------------------

class TestAutochiusuraEAccoppiati:

    def test_autochiuso_non_si_accoppia_con_end_successivo(self) -> None:
        sorgente = (
            '{{< figure url="/a.jpg" />}}\n\n'
            '{{< figure url="/b.jpg" >}}didascalia{{< end >}}'
        )
        html = shortcodes.renderizza(sorgente)

        assert '<img src="/a.jpg"' in html
        assert "<figcaption>didascalia</figcaption>" in html
        assert "{{<" not in html


    def test_apertura_senza_end_resta_invariata(self) -> None:
        sorgente = '{{< figure url="/a.jpg" >}}'

        assert shortcodes.renderizza(sorgente) == sorgente


# ---------------------------------------------------------------------------
# Test: robustezza
# ---------------------------------------------------------------------------

class TestRobustezza:

    def test_template_mancante_lascia_invariato(self) -> None:
        sorgente = '{{< fantasma url="/x" />}}'
        html = shortcodes.renderizza(sorgente)

        assert html == sorgente


    def test_tag_end_isolato_non_e_uno_shortcode(self) -> None:
        html = shortcodes.renderizza("{{< end >}}")

        assert html == "{{< end >}}"


    def test_testo_senza_shortcode_invariato(self) -> None:
        sorgente = "# Titolo\n\nNessuno shortcode qui."

        assert shortcodes.renderizza(sorgente) == sorgente


    def test_jinja2_mancante_solleva_importerror(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(sys.modules, "jinja2", None)

        with pytest.raises(ImportError):
            ProcessoreShortcode()
