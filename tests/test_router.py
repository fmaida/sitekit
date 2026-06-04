from pathlib import Path
from unittest.mock import MagicMock

import pytest

from sitekit.router import Router
from sitekit.settings import settings

FRONTMATTER_CON_TEMPLATE = "---\ntitle: Pagina\ntemplate: about\n---\n# Pagina"
FRONTMATTER_TEMPLATE_CON_ESTENSIONE = "---\ntitle: Pagina\ntemplate: about.html\n---\n# Pagina"
FRONTMATTER_SENZA_TEMPLATE = "---\ntitle: Pagina\n---\n# Pagina"


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    """Restituisce una cartella base temporanea."""
    return tmp_path


@pytest.fixture()
def router(base: Path) -> Router:
    """Istanza di Router puntata sulla cartella temporanea."""
    return Router(base)


def crea_file(base: Path, *parti: str, contenuto: str = "") -> Path:
    """Crea il file (e le directory intermedie) e lo restituisce."""
    percorso = base.joinpath(*parti)
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(contenuto, encoding="utf-8")

    return percorso


# ---------------------------------------------------------------------------
# __init__ — cartella_base opzionale
# ---------------------------------------------------------------------------


class TestInit:

    def test_default_usa_content_dir(self) -> None:
        """Senza cartella_base il Router usa settings.CONTENT_DIR."""
        router = Router()

        assert router.base == settings.CONTENT_DIR.resolve()

    def test_cartella_base_esplicita(self, base: Path) -> None:
        """Con cartella_base esplicita viene usata quella."""
        router = Router(base)

        assert router.base == base.resolve()


# ---------------------------------------------------------------------------
# da_url — lingua di default
# ---------------------------------------------------------------------------


class TestDaUrlDefault:

    def test_url_semplice(self, router: Router, base: Path) -> None:
        crea_file(base, "chi-siamo", "index.md")

        path, _ = router.da_url("/chi-siamo")

        assert path == base / "chi-siamo" / "index.md"

    def test_url_annidato(self, router: Router, base: Path) -> None:
        crea_file(base, "cartella", "sottocartella", "index.md")

        path, _ = router.da_url("/cartella/sottocartella")

        assert path == base / "cartella" / "sottocartella" / "index.md"

    def test_url_homepage(self, router: Router, base: Path) -> None:
        crea_file(base, "index.md")

        path, _ = router.da_url("/")

        assert path == base / "index.md"

    def test_url_con_slash_finale(self, router: Router, base: Path) -> None:
        crea_file(base, "chi-siamo", "index.md")

        path, _ = router.da_url("/chi-siamo/")

        assert path == base / "chi-siamo" / "index.md"


# ---------------------------------------------------------------------------
# da_url — lingua prefissata
# ---------------------------------------------------------------------------


class TestDaUrlLinguaPrefissata:

    def test_url_con_lingua(self, router: Router, base: Path) -> None:
        crea_file(base, "chi-siamo", "index.en.md")

        path, _ = router.da_url("/en/chi-siamo")

        assert path == base / "chi-siamo" / "index.en.md"

    def test_url_annidato_con_lingua(
        self, router: Router, base: Path
    ) -> None:
        crea_file(base, "cartella", "sottocartella", "index.en.md")

        path, _ = router.da_url("/en/cartella/sottocartella")

        assert path == base / "cartella" / "sottocartella" / "index.en.md"

    def test_url_homepage_con_lingua(
        self, router: Router, base: Path
    ) -> None:
        crea_file(base, "index.en.md")

        path, _ = router.da_url("/en/")

        assert path == base / "index.en.md"

    def test_segmento_tre_caratteri_trattato_come_path(
        self, router: Router, base: Path
    ) -> None:
        crea_file(base, "blog", "articolo", "index.md")

        path, _ = router.da_url("/blog/articolo")

        assert path == base / "blog" / "articolo" / "index.md"


# ---------------------------------------------------------------------------
# da_url — fallback _index
# ---------------------------------------------------------------------------


class TestDaUrlIndexFallback:

    def test_fallback_underscore_index(
        self, router: Router, base: Path
    ) -> None:
        """Se index.md non esiste, usa _index.md."""
        crea_file(base, "chi-siamo", "_index.md")

        path, _ = router.da_url("/chi-siamo")

        assert path == base / "chi-siamo" / "_index.md"

    def test_fallback_underscore_index_con_lingua(
        self, router: Router, base: Path
    ) -> None:
        """Se index.en.md non esiste, usa _index.en.md."""
        crea_file(base, "chi-siamo", "_index.en.md")

        path, _ = router.da_url("/en/chi-siamo")

        assert path == base / "chi-siamo" / "_index.en.md"

    def test_index_ha_priorita_su_underscore_index(
        self, router: Router, base: Path
    ) -> None:
        """index.md ha priorità su _index.md."""
        crea_file(base, "chi-siamo", "index.md")
        crea_file(base, "chi-siamo", "_index.md")

        path, _ = router.da_url("/chi-siamo")

        assert path == base / "chi-siamo" / "index.md"


# ---------------------------------------------------------------------------
# da_url — template
# ---------------------------------------------------------------------------


class TestDaUrlTemplate:

    def test_template_letto_dal_frontmatter(
        self, router: Router, base: Path
    ) -> None:
        """Il template viene letto dal campo 'template' nel frontmatter."""
        crea_file(base, "chi-siamo", "index.md", contenuto=FRONTMATTER_CON_TEMPLATE)

        _, template = router.da_url("/chi-siamo")

        assert template == "about.html"

    def test_template_letto_con_estensione_html_aggiunta(
        self, router: Router, base: Path
    ) -> None:
        """Se il template non finisce con .html, viene aggiunto."""
        crea_file(base, "chi-siamo", "index.md", contenuto=FRONTMATTER_CON_TEMPLATE)

        _, template = router.da_url("/chi-siamo")

        assert template == "about.html"

    def test_template_con_estensione_html_gia_presente(
        self, router: Router, base: Path
    ) -> None:
        """Se il template ha già .html, non viene duplicata."""
        crea_file(
            base, "chi-siamo", "index.md",
            contenuto=FRONTMATTER_TEMPLATE_CON_ESTENSIONE,
        )

        _, template = router.da_url("/chi-siamo")

        assert template == "about.html"

    def test_template_default_se_campo_assente(
        self, router: Router, base: Path
    ) -> None:
        """Se il frontmatter non ha 'template', il default è single.html."""
        crea_file(base, "chi-siamo", "index.md", contenuto=FRONTMATTER_SENZA_TEMPLATE)

        _, template = router.da_url("/chi-siamo")

        assert template == "single.html"

    def test_template_default_homepage_senza_template(
        self, router: Router, base: Path
    ) -> None:
        """La homepage senza template usa home.html come default."""
        crea_file(base, "index.md", contenuto=FRONTMATTER_SENZA_TEMPLATE)

        _, template = router.da_url("/")

        assert template == "home.html"

    def test_template_homepage_con_template_esplicito(
        self, router: Router, base: Path
    ) -> None:
        """La homepage con template esplicito usa quello, non home.html."""
        crea_file(base, "index.md", contenuto=FRONTMATTER_CON_TEMPLATE)

        _, template = router.da_url("/")

        assert template == "about.html"

    def test_template_da_underscore_index(
        self, router: Router, base: Path
    ) -> None:
        """Il template viene letto anche da _index.md."""
        crea_file(base, "chi-siamo", "_index.md", contenuto=FRONTMATTER_CON_TEMPLATE)

        _, template = router.da_url("/chi-siamo")

        assert template == "about"

    def test_template_da_file_lingua(
        self, router: Router, base: Path
    ) -> None:
        """Il template viene letto dal file localizzato index.en.md."""
        crea_file(base, "chi-siamo", "index.en.md", contenuto=FRONTMATTER_CON_TEMPLATE)

        _, template = router.da_url("/en/chi-siamo")

        assert template == "about"


# ---------------------------------------------------------------------------
# da_url — alias
# ---------------------------------------------------------------------------


class TestDaUrlAlias:

    def test_alias_risolve_a_cartella_destinazione(
        self, router: Router, base: Path
    ) -> None:
        """Un alias deve ritornare il percorso della cartella di destinazione."""
        crea_file(base, "chi-siamo", "index.en.md")
        router.aggiungi_alias("about-us", "chi-siamo")

        path, _ = router.da_url("/en/about-us")

        assert path == base / "chi-siamo" / "index.en.md"

    def test_file_esistente_ha_priorita_sull_alias(
        self, router: Router, base: Path
    ) -> None:
        """Se il file esiste su disco, viene restituito senza cercare alias."""
        crea_file(base, "about-us", "index.en.md")
        crea_file(base, "chi-siamo", "index.en.md")
        router.aggiungi_alias("about-us", "chi-siamo")

        path, _ = router.da_url("/en/about-us")

        assert path == base / "about-us" / "index.en.md"

    def test_alias_su_lingua_default(
        self, router: Router, base: Path
    ) -> None:
        """Gli alias funzionano anche per la lingua di default."""
        crea_file(base, "chi-siamo", "index.md")
        router.aggiungi_alias("about-us", "chi-siamo")

        path, _ = router.da_url("/about-us")

        assert path == base / "chi-siamo" / "index.md"

    def test_alias_con_underscore_index(
        self, router: Router, base: Path
    ) -> None:
        """L'alias funziona anche quando la destinazione ha _index.md."""
        crea_file(base, "servizi", "_index.md")
        router.aggiungi_alias("services", "servizi")

        path, _ = router.da_url("/services")

        assert path == base / "servizi" / "_index.md"

    def test_file_non_trovato_e_nessun_alias_solleva_errore(
        self, router: Router
    ) -> None:
        """Senza file né alias, deve sollevare FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            router.da_url("/en/about-us")


# ---------------------------------------------------------------------------
# da_url — sicurezza
# ---------------------------------------------------------------------------


class TestDaUrlSicurezza:

    def test_path_traversal_solleva_errore(self, router: Router) -> None:
        with pytest.raises(ValueError, match="cartella base"):
            router.da_url("/../../segreto")


# ---------------------------------------------------------------------------
# verso_url — lingua di default
# ---------------------------------------------------------------------------


class TestVersoUrlDefault:

    def test_percorso_semplice(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "chi-siamo", "index.md")

        assert router.verso_url(percorso) == "/chi-siamo/"

    def test_percorso_annidato(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "cartella", "sottocartella", "index.md")

        assert router.verso_url(percorso) == "/cartella/sottocartella/"

    def test_homepage_default(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "index.md")

        assert router.verso_url(percorso) == "/"

    def test_underscore_index(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "chi-siamo", "_index.md")

        assert router.verso_url(percorso) == "/chi-siamo/"


# ---------------------------------------------------------------------------
# verso_url — lingua prefissata
# ---------------------------------------------------------------------------


class TestVersoUrlLinguaPrefissata:

    def test_percorso_con_lingua(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "chi-siamo", "index.en.md")

        assert router.verso_url(percorso) == "/en/chi-siamo/"

    def test_homepage_con_lingua(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "index.en.md")

        assert router.verso_url(percorso) == "/en/"

    def test_underscore_index_con_lingua(
        self, router: Router, base: Path
    ) -> None:
        percorso = crea_file(base, "chi-siamo", "_index.en.md")

        assert router.verso_url(percorso) == "/en/chi-siamo/"


# ---------------------------------------------------------------------------
# verso_url — errori
# ---------------------------------------------------------------------------


class TestVersoUrlErrori:

    def test_nome_non_convenzionale_solleva_errore(
        self, router: Router, base: Path
    ) -> None:
        percorso = crea_file(base, "pagina.md")

        with pytest.raises(ValueError, match="convenzione"):
            router.verso_url(percorso)

    def test_percorso_fuori_base_solleva_errore(
        self, router: Router, tmp_path: Path
    ) -> None:
        percorso_esterno = tmp_path.parent / "segreto" / "index.md"

        with pytest.raises(ValueError, match="cartella base"):
            router.verso_url(percorso_esterno)


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


class TestRegister:

    def test_register_aggiunge_globale_jinja2(self, router: Router) -> None:
        app_mock = MagicMock()

        router.register(app_mock)

        app_mock.jinja_env.globals.__setitem__.assert_called_once_with(
            "router", router
        )
