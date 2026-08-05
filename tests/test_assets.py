from pathlib import Path

import pytest

from sitekit import assets
from sitekit.settings import settings


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def cartelle_isolate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Sposta le quattro cartelle della pipeline su tmp_path, così ogni
    test lavora su un albero pulito.
    """

    monkeypatch.setattr(settings, "CACHE_DIR", tmp_path / ".cache")
    monkeypatch.setattr(settings, "RESOURCES_DIR", tmp_path / "resources")
    monkeypatch.setattr(settings, "STATIC_DIR", tmp_path / "static")
    monkeypatch.setattr(settings, "ASSETS_DIR", tmp_path / "assets")
    monkeypatch.setattr(settings, "ASSETS_URL", "/assets")
    monkeypatch.setattr(settings, "VERBOSE", False)

    (tmp_path / ".cache").mkdir()


def _scrivi(percorso: Path, contenuto: str = "x") -> Path:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(contenuto, encoding="utf-8")

    return percorso


# ---------------------------------------------------------------------------
# destinazione() e url()
# ---------------------------------------------------------------------------

class TestPercorsi:

    def test_destinazione_dentro_la_cache(self) -> None:
        percorso = assets.destinazione("images/chi-siamo")

        assert percorso == settings.CACHE_DIR / "assets" / "images" / "chi-siamo"
        assert percorso.is_dir()


    def test_destinazione_senza_argomenti(self) -> None:
        assert assets.destinazione() == settings.CACHE_DIR / "assets"


    def test_url_prefissato(self) -> None:
        assert assets.url("images/chi-siamo") == "/assets/images/chi-siamo"


    def test_url_senza_argomenti(self) -> None:
        assert assets.url() == "/assets"


    def test_url_normalizza_gli_slash(self) -> None:
        assert assets.url("/images//chi-siamo/") == "/assets/images/chi-siamo"


    def test_url_rispetta_assets_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "ASSETS_URL", "/risorse/")

        assert assets.url("images/x") == "/risorse/images/x"


    def test_destinazione_e_url_descrivono_lo_stesso_percorso(self) -> None:
        """
        È l'invariante che tiene insieme la pipeline: ciò che si
        scrive su disco e ciò che si stampa nel markup devono
        riferirsi allo stesso posto.
        """

        sotto = "images/blog/primo-post"
        su_disco = assets.destinazione(sotto).relative_to(assets.cartella_generati())
        nell_url = assets.url(sotto).removeprefix(settings.ASSETS_URL + "/")

        assert su_disco.as_posix() == nell_url


# ---------------------------------------------------------------------------
# build()
# ---------------------------------------------------------------------------

class TestBuild:

    def test_unisce_le_tre_sorgenti(self, tmp_path: Path) -> None:
        _scrivi(assets.cartella_generati() / "images" / "foto__800.jpg")
        _scrivi(settings.RESOURCES_DIR / "images" / "logo.png")
        _scrivi(settings.STATIC_DIR / "css" / "style.css")

        assets.build()

        assert (settings.ASSETS_DIR / "images" / "foto__800.jpg").is_file()
        assert (settings.ASSETS_DIR / "images" / "logo.png").is_file()
        assert (settings.ASSETS_DIR / "css" / "style.css").is_file()


    def test_preserva_la_struttura_di_primo_livello(self) -> None:
        _scrivi(settings.STATIC_DIR / "fonts" / "inter.woff2")
        _scrivi(settings.STATIC_DIR / "favicon.ico")

        assets.build()

        assert (settings.ASSETS_DIR / "fonts" / "inter.woff2").is_file()
        assert (settings.ASSETS_DIR / "favicon.ico").is_file()


    def test_restituisce_il_numero_di_file_copiati(self) -> None:
        _scrivi(settings.STATIC_DIR / "css" / "a.css")
        _scrivi(settings.STATIC_DIR / "css" / "b.css")

        assert assets.build() == 2


    def test_e_incrementale(self) -> None:
        _scrivi(settings.STATIC_DIR / "css" / "style.css")

        assert assets.build() == 1
        assert assets.build() == 0


    def test_ricopia_un_file_modificato(self) -> None:
        sorgente = _scrivi(settings.STATIC_DIR / "css" / "style.css", "prima")
        assets.build()

        sorgente.write_text("dopo", encoding="utf-8")

        assert assets.build() == 1
        assert (settings.ASSETS_DIR / "css" / "style.css").read_text() == "dopo"


    def test_sorgente_mancante_non_e_un_errore(self) -> None:
        _scrivi(settings.STATIC_DIR / "css" / "style.css")

        # RESOURCES_DIR non esiste affatto
        assert not settings.RESOURCES_DIR.exists()
        assert assets.build() == 1


    def test_a_parita_di_percorso_vince_static(self) -> None:
        _scrivi(settings.RESOURCES_DIR / "css" / "style.css", "da resources")
        _scrivi(settings.STATIC_DIR / "css" / "style.css", "da static")

        assets.build()

        assert (settings.ASSETS_DIR / "css" / "style.css").read_text() == "da static"


    def test_la_collisione_viene_segnalata_in_verbose(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        monkeypatch.setattr(settings, "VERBOSE", True)
        _scrivi(settings.RESOURCES_DIR / "css" / "style.css", "da resources")
        _scrivi(settings.STATIC_DIR / "css" / "style.css", "da static")

        assets.build()

        assert "conflitto" in capsys.readouterr().out


    def test_pulisci_rimuove_gli_orfani(self) -> None:
        _scrivi(settings.STATIC_DIR / "css" / "style.css")
        assets.build()

        orfano = _scrivi(settings.ASSETS_DIR / "css" / "vecchio.css")

        assets.build(pulisci=True)

        assert not orfano.exists()
        assert (settings.ASSETS_DIR / "css" / "style.css").is_file()


    def test_senza_pulisci_gli_orfani_restano(self) -> None:
        _scrivi(settings.STATIC_DIR / "css" / "style.css")
        orfano = _scrivi(settings.ASSETS_DIR / "css" / "vecchio.css")

        assets.build()

        assert orfano.exists()


    def test_pulisci_rimuove_le_cartelle_vuote(self) -> None:
        _scrivi(settings.STATIC_DIR / "css" / "style.css")
        _scrivi(settings.ASSETS_DIR / "vecchia" / "roba.txt")

        assets.build(pulisci=True)

        assert not (settings.ASSETS_DIR / "vecchia").exists()


    def test_assets_dir_fuori_da_base_dir(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        altrove = tmp_path.parent / f"{tmp_path.name}-altrove"
        monkeypatch.setattr(settings, "ASSETS_DIR", altrove)
        _scrivi(settings.STATIC_DIR / "css" / "style.css")

        assets.build()

        assert (altrove / "css" / "style.css").is_file()


    def test_destinazione_annidata_in_una_sorgente(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Se ASSETS_DIR sta dentro STATIC_DIR, l'unione non deve
        ricopiarsi addosso a se stessa all'infinito.
        """

        monkeypatch.setattr(settings, "ASSETS_DIR", settings.STATIC_DIR / "out")
        _scrivi(settings.STATIC_DIR / "css" / "style.css")

        assets.build()
        secondo_giro = assets.build()

        assert (settings.ASSETS_DIR / "css" / "style.css").is_file()
        assert secondo_giro == 0
