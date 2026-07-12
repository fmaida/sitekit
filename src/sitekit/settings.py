from dataclasses import dataclass
from pathlib import Path
from babel import Locale

@dataclass
class SettingsClass:

    # Risali a partire dalla working directory corrente
    # fino a trovare pyproject.toml
    @staticmethod
    def _get_base_dir() -> Path:
        cur = Path.cwd().resolve()
        for parent in [cur, *cur.parents]:
            if (parent / "pyproject.toml").exists():
                return parent
        raise RuntimeError("Non trovo la root del progetto (pyproject.toml mancante?)")

    def _carica_lingue_disponibili(self):
        """
        Carica le lingue tradotte disponibili.

        returns:
            list: Una lista di lingue disponibili.
        """
        lingue = []

        # Carica le lingue dal file locale
        if self.I18N_DIR.exists() and self.I18N_DIR.is_dir():
            for file in self.I18N_DIR.iterdir():
                if file.is_file() and file.suffix == ".json":
                    id_lingua = file.stem
                    nome_lingua = Locale.parse(id_lingua).get_display_name()
                    lingue.append((id_lingua,
                                   nome_lingua))

        # Ordina le lingue in ordine alfabetico in base al nome completo della lingua
        lingue.sort(key=lambda x: x[1])

        return lingue

    def set_i18n_dir(self, path: Path):
        self.I18N_DIR = path
        self.SITE_LANGUAGES = self._carica_lingue_disponibili()
        self.SITE_LANGUAGE_CODES = [codice for codice, _ in self.SITE_LANGUAGES]
        self.SITE_LANGUAGE_NAMES = [nome for _, nome in self.SITE_LANGUAGES]

    def __init__(self):
        self.BASE_DIR = SettingsClass._get_base_dir()
        self.BASE_URL = "https://example.com"
        self.CACHE_DIR = self.BASE_DIR / ".cache"
        self.CONTENT_DIR = self.BASE_DIR / "content"
        self.BUILD_DIR = self.BASE_DIR / "build"
        self.set_i18n_dir(self.BASE_DIR / "i18n")
        self.STATIC_DIR = self.BASE_DIR / "static"
        self.STATIC_CONTENT = "/static"
        self.TEMPLATES_DIR = self.BASE_DIR / "templates"
        self.PLUGINS_DIR = self.TEMPLATES_DIR / "plugins"
        self.SITE_LANGUAGES = self._carica_lingue_disponibili()
        self.VERBOSE = False

settings = SettingsClass()