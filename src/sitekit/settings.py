from dataclasses import dataclass
from pathlib import Path
from babel import Locale

@dataclass
class SettingsClass:

    # Risali a partire dal file corrente
    # (__file__) fino a trovare pyproject.toml
    @staticmethod
    def _get_base_dir() -> Path:
        cur = Path(__file__).resolve()
        for parent in [cur, *cur.parents]:
            if (parent / "pyproject.toml").exists():
                return parent
        raise RuntimeError("Non trovo la root del progetto (pyproject.toml mancante?)")

    def carica_lingue_disponibili(self):
        """
        Carica le lingue tradotte disponibili.

        returns:
            list: Una lista di lingue disponibili.
        """
        lingue = []

        # Carica le lingue dal file locale
        if self.LOCALE_DIR.exists() and self.LOCALE_DIR.is_dir():
            for file in self.LOCALE_DIR.iterdir():
                if file.is_file() and file.suffix == ".json":
                    id_lingua = file.stem
                    nome_lingua = Locale.parse(id_lingua).get_display_name()
                    lingue.append((id_lingua,
                                   nome_lingua))

        # Ordina le lingue in ordine alfabetico in base al nome completo della lingua
        lingue.sort(key=lambda x: x[1])

        return lingue

    def __init__(self):
        self.BASE_DIR = SettingsClass._get_base_dir()
        self.BASE_URL = "https://venice.bio"
        self.CACHE_DIR = self.BASE_DIR / ".cache"
        self.CONTENT_DIR = self.BASE_DIR / "content"
        self.BUILD_DIR = self.BASE_DIR / "build"
        self.LOCALE_DIR = self.BASE_DIR / "locale"
        self.STATIC_DIR = self.BASE_DIR / "static"
        self.TEMPLATES_DIR = self.BASE_DIR / "templates"
        self.SITE_LANGUAGES = self.carica_lingue_disponibili()
        self.SITE_LANGUAGE_CODES = [codice for codice, _ in self.SITE_LANGUAGES]
        self.SITE_LANGUAGE_NAMES = [nome for _, nome in self.SITE_LANGUAGES]
        self.VERBOSE = False

settings = SettingsClass()