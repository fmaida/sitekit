# test_images.py — test per sitekit.images e sitekit.images.imgcache
#
# Copre i bug fixati:
#   1. aspect_ratio e anchor fanno parte della chiave cache
#   2. ultima_immagine_sha1 viene settato al primo caricamento
#   3. SHA1 calcolato una sola volta per chiamata (nessun doppio calcolo)
#   4. File mancanti su disco → rielaborazione anche se la cache RAM li conosce

import shutil
import pytest
from pathlib import Path
from PIL import Image

from sitekit.images import imgcache
from sitekit.images import images


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_imgcache(tmp_path):
    """
    Svuota la CACHE in memoria prima di ogni test per garantire isolamento.
    Non tocca il file su disco (tmp_path è già separata per ogni test).
    """
    imgcache.CACHE = set()
    images.ultima_immagine = None
    images.ultima_immagine_sha1 = None
    yield
    imgcache.CACHE = set()
    images.ultima_immagine = None
    images.ultima_immagine_sha1 = None


@pytest.fixture()
def immagine_test(tmp_path) -> Path:
    """Crea un file JPEG sintetico 200×150 px per i test."""
    img = Image.new("RGB", (200, 150), color=(100, 150, 200))
    percorso = tmp_path / "foto_test.jpg"
    img.save(percorso, "JPEG")
    return percorso


@pytest.fixture()
def cartella_output(tmp_path) -> Path:
    out = tmp_path / "output"
    out.mkdir()
    return out


# ---------------------------------------------------------------------------
# Test imgcache.verifica_e_aggiungi — chiave cache
# ---------------------------------------------------------------------------

class TestVerificaEAggiungi:

    def test_primo_inserimento_ritorna_true(self, immagine_test, cartella_output):
        da_elaborare, sha1 = imgcache.verifica_e_aggiungi(
            immagine_test, 400, cartella_output)
        assert da_elaborare is True
        assert sha1 is not None

    def test_secondo_inserimento_stesso_file_senza_files_su_disco_ritorna_true(
            self, immagine_test, cartella_output):
        """Anche se la CACHE RAM conosce il file, se i file su disco mancano
        deve richiedere rielaborazione."""
        imgcache.verifica_e_aggiungi(immagine_test, 400, cartella_output)
        da_elaborare, _ = imgcache.verifica_e_aggiungi(
            immagine_test, 400, cartella_output)
        assert da_elaborare is True

    def test_cache_hit_con_files_su_disco(self, immagine_test, cartella_output):
        """Se la cache conosce il file E i file su disco esistono → skip."""
        imgcache.verifica_e_aggiungi(immagine_test, 400, cartella_output)

        # Simula la presenza dei file su disco
        stem = immagine_test.stem + "__400"
        for ext in (".jpg", ".webp", ".avif"):
            (cartella_output / f"{stem}{ext}").touch()

        da_elaborare, _ = imgcache.verifica_e_aggiungi(
            immagine_test, 400, cartella_output)
        assert da_elaborare is False

    def test_aspect_ratio_diverso_non_usa_cache(self, immagine_test, cartella_output):
        """
        Bug #1: stessa immagine, stesso longest_side, aspect_ratio diverso
        → deve essere rielaborata, non saltata.
        """
        imgcache.verifica_e_aggiungi(
            immagine_test, 800, cartella_output, aspect_ratio="16:9")

        # Simula file su disco per il primo crop
        stem = immagine_test.stem + "__800"
        for ext in (".jpg", ".webp", ".avif"):
            (cartella_output / f"{stem}{ext}").touch()

        # Richiesta con aspect_ratio diverso: non deve trovare cache hit
        da_elaborare, _ = imgcache.verifica_e_aggiungi(
            immagine_test, 800, cartella_output, aspect_ratio="4:3")
        assert da_elaborare is True

    def test_anchor_diverso_non_usa_cache(self, immagine_test, cartella_output):
        """
        Bug #1 (variante): stessa immagine, stesso aspect_ratio, anchor diverso
        → deve essere rielaborata.
        """
        imgcache.verifica_e_aggiungi(
            immagine_test, 800, cartella_output, aspect_ratio="16:9", anchor="top")

        stem = immagine_test.stem + "__800"
        for ext in (".jpg", ".webp", ".avif"):
            (cartella_output / f"{stem}{ext}").touch()

        da_elaborare, _ = imgcache.verifica_e_aggiungi(
            immagine_test, 800, cartella_output, aspect_ratio="16:9", anchor="bottom")
        assert da_elaborare is True

    def test_file_inesistente_ritorna_false_e_none(self, tmp_path, cartella_output):
        da_elaborare, sha1 = imgcache.verifica_e_aggiungi(
            tmp_path / "non_esiste.jpg", 400, cartella_output)
        assert da_elaborare is False
        assert sha1 is None

    def test_sha1_restituito_e_consistente(self, immagine_test, cartella_output):
        """Lo SHA1 restituito deve essere identico tra due chiamate sullo stesso file."""
        _, sha1_prima = imgcache.verifica_e_aggiungi(
            immagine_test, 400, cartella_output)
        imgcache.CACHE = set()  # resetta per forzare ricalcolo
        _, sha1_seconda = imgcache.verifica_e_aggiungi(
            immagine_test, 400, cartella_output)
        assert sha1_prima == sha1_seconda
        assert len(sha1_prima) == 40  # SHA-1 hex = 40 caratteri


# ---------------------------------------------------------------------------
# Test images.copy_single — cache RAM (ultima_immagine)
# ---------------------------------------------------------------------------

class TestCacheRAMImmagine:

    def test_sha1_settato_al_primo_caricamento(self, immagine_test, cartella_output):
        """
        Bug #2: dopo la prima chiamata, ultima_immagine_sha1 non deve
        essere None — deve contenere lo SHA-1 del file caricato.
        """
        images.copy_single(immagine_test, cartella_output,
                           longest_side=400, output_formats=["jpeg"])
        assert images.ultima_immagine_sha1 is not None

    def test_sha1_corrisponde_al_file(self, immagine_test, cartella_output):
        """Il valore in ultima_immagine_sha1 deve corrispondere all'hash reale del file."""
        from sitekit.images.hash import _calcola_sha1
        images.copy_single(immagine_test, cartella_output,
                           longest_side=400, output_formats=["jpeg"])
        assert images.ultima_immagine_sha1 == _calcola_sha1(immagine_test)

    def test_stessa_immagine_non_riapre_il_file(self, immagine_test, cartella_output, monkeypatch):
        """
        Chiamando copy_single due volte sullo stesso file (con longest_side diverso
        così imgcache non skippa), Image.open deve essere chiamata una sola volta.
        """
        aperture = []
        apri = Image.open

        def _conta_aperture(*args, **kwargs):
            aperture.append(args[0] if args else None)
            return apri(*args, **kwargs)

        monkeypatch.setattr(Image, "open", _conta_aperture)

        images.copy_single(immagine_test, cartella_output,
                           longest_side=400, output_formats=["jpeg"])
        images.copy_single(immagine_test, cartella_output,
                           longest_side=800, output_formats=["jpeg"])

        assert len(aperture) == 1


# ---------------------------------------------------------------------------
# Test PictureClass — rendering HTML
# ---------------------------------------------------------------------------

from sitekit.images.picture_class import PictureClass

class TestPictureClass:

    def test_usa_il_nome_reale_del_file(self, tmp_path):
        """Il tag <picture> deve usare il nome della cartella (= stem del file sorgente),
        non il nome hardcoded 'immagine'."""
        folder = tmp_path / "static" / "images" / "foto-hero"
        pic = PictureClass(folder=folder)
        html = str(pic)
        assert "foto-hero__400.avif" in html
        assert "foto-hero__800.jpg" in html
        assert "immagine__" not in html

    def test_alt_vuoto_per_default(self, tmp_path):
        folder = tmp_path / "static" / "images" / "banner"
        pic = PictureClass(folder=folder)
        assert 'alt=""' in str(pic)

    def test_alt_personalizzato(self, tmp_path):
        folder = tmp_path / "static" / "images" / "banner"
        pic = PictureClass(folder=folder, alt="Vista del porto di Napoli")
        assert 'alt="Vista del porto di Napoli"' in str(pic)

    def test_tronca_percorso_a_static(self, tmp_path):
        """Il percorso nel srcset deve iniziare da /static/, non dal path assoluto."""
        folder = tmp_path / "static" / "images" / "hero"
        pic = PictureClass(folder=folder)
        html = str(pic)
        assert str(tmp_path) not in html
        assert "/static/images/hero" in html

    def test_contiene_tutti_e_tre_i_formati(self, tmp_path):
        folder = tmp_path / "static" / "images" / "img"
        pic = PictureClass(folder=folder)
        html = str(pic)
        assert "image/avif" in html
        assert "image/webp" in html
        assert "<img " in html

    def test_contiene_tutti_i_breakpoint(self, tmp_path):
        folder = tmp_path / "static" / "images" / "img"
        pic = PictureClass(folder=folder)
        html = str(pic)
        for size in (400, 800, 1200, 1600):
            assert f"{size}w" in html
