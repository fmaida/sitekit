from pathlib import Path
from unittest.mock import MagicMock

import pytest

from sitekit.router import Router


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    """Restituisce una cartella base temporanea."""
    return tmp_path


@pytest.fixture()
def router(base: Path) -> Router:
    """Istanza di Router puntata sulla cartella temporanea."""
    return Router(base)


def crea_file(base: Path, *parti: str) -> Path:
    """Crea il file (e le directory intermedie) e lo restituisce."""
    percorso = base.joinpath(*parti)
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.touch()

    return percorso


# ---------------------------------------------------------------------------
# da_url — lingua di default
# ---------------------------------------------------------------------------


class TestRestituisciPercorsoDefault:

    def test_url_semplice(self, router: Router, base: Path) -> None:
        crea_file(base, "chi-siamo", "index.md")

        assert router.da_url("/chi-siamo") == (
            base / "chi-siamo" / "index.md"
        )

    def test_url_annidato(self, router: Router, base: Path) -> None:
        crea_file(base, "cartella", "sottocartella", "index.md")

        assert router.da_url("/cartella/sottocartella") == (
            base / "cartella" / "sottocartella" / "index.md"
        )

    def test_url_homepage(self, router: Router, base: Path) -> None:
        """URL radice → index.md senza verifica di esistenza."""
        assert router.da_url("/") == base / "index.md"

    def test_url_con_slash_finale(self, router: Router, base: Path) -> None:
        crea_file(base, "chi-siamo", "index.md")

        assert router.da_url("/chi-siamo/") == (
            base / "chi-siamo" / "index.md"
        )


# ---------------------------------------------------------------------------
# da_url — lingua prefissata
# ---------------------------------------------------------------------------


class TestRestituisciPercorsoLinguaPrefissata:

    def test_url_con_lingua(self, router: Router, base: Path) -> None:
        crea_file(base, "chi-siamo", "index.en.md")

        assert router.da_url("/en/chi-siamo") == (
            base / "chi-siamo" / "index.en.md"
        )

    def test_url_annidato_con_lingua(
        self, router: Router, base: Path
    ) -> None:
        crea_file(base, "cartella", "sottocartella", "index.en.md")

        assert router.da_url("/en/cartella/sottocartella") == (
            base / "cartella" / "sottocartella" / "index.en.md"
        )

    def test_url_homepage_con_lingua(
        self, router: Router, base: Path
    ) -> None:
        """URL /en/ → index.en.md senza verifica di esistenza."""
        assert router.da_url("/en/") == base / "index.en.md"

    def test_segmento_tre_caratteri_trattato_come_path(
        self, router: Router, base: Path
    ) -> None:
        crea_file(base, "blog", "articolo", "index.md")

        assert router.da_url("/blog/articolo") == (
            base / "blog" / "articolo" / "index.md"
        )


# ---------------------------------------------------------------------------
# da_url — alias
# ---------------------------------------------------------------------------


class TestRestituisciPercorsoAlias:

    def test_alias_risolve_a_cartella_destinazione(
        self, router: Router, base: Path
    ) -> None:
        """Un alias deve ritornare il percorso della cartella di destinazione."""
        crea_file(base, "chi-siamo", "index.en.md")
        router.aggiungi_alias("about-us", "chi-siamo")

        assert router.da_url("/en/about-us") == (
            base / "chi-siamo" / "index.en.md"
        )

    def test_file_esistente_ha_priorita_sull_alias(
        self, router: Router, base: Path
    ) -> None:
        """Se il file esiste su disco, viene restituito senza cercare alias."""
        crea_file(base, "about-us", "index.en.md")
        crea_file(base, "chi-siamo", "index.en.md")
        router.aggiungi_alias("about-us", "chi-siamo")

        assert router.da_url("/en/about-us") == (
            base / "about-us" / "index.en.md"
        )

    def test_alias_su_lingua_default(
        self, router: Router, base: Path
    ) -> None:
        """Gli alias funzionano anche per la lingua di default."""
        crea_file(base, "chi-siamo", "index.md")
        router.aggiungi_alias("about-us", "chi-siamo")

        assert router.da_url("/about-us") == (
            base / "chi-siamo" / "index.md"
        )

    def test_file_non_trovato_e_nessun_alias_solleva_errore(
        self, router: Router
    ) -> None:
        """Senza file né alias, deve sollevare FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            router.da_url("/en/about-us")


# ---------------------------------------------------------------------------
# da_url — sicurezza
# ---------------------------------------------------------------------------


class TestRestituisciPercorsoSicurezza:

    def test_path_traversal_solleva_errore(self, router: Router) -> None:
        with pytest.raises(ValueError, match="cartella base"):
            router.da_url("/../../segreto")


# ---------------------------------------------------------------------------
# verso_url — lingua di default
# ---------------------------------------------------------------------------


class TestRestituisciUrlDefault:

    def test_percorso_semplice(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "chi-siamo", "index.md")

        assert router.verso_url(percorso) == "/chi-siamo/"

    def test_percorso_annidato(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "cartella", "sottocartella", "index.md")

        assert router.verso_url(percorso) == "/cartella/sottocartella/"

    def test_homepage_default(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "index.md")

        assert router.verso_url(percorso) == "/"


# ---------------------------------------------------------------------------
# verso_url — lingua prefissata
# ---------------------------------------------------------------------------


class TestRestituisciUrlLinguaPrefissata:

    def test_percorso_con_lingua(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "chi-siamo", "index.en.md")

        assert router.verso_url(percorso) == "/en/chi-siamo/"

    def test_homepage_con_lingua(self, router: Router, base: Path) -> None:
        percorso = crea_file(base, "index.en.md")

        assert router.verso_url(percorso) == "/en/"


# ---------------------------------------------------------------------------
# verso_url — errori
# ---------------------------------------------------------------------------


class TestRestituisciUrlErrori:

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
