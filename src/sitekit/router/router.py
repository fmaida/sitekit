from pathlib import Path

from sitekit.settings import settings


class Router:
    """
    Risolve URL multilingua in percorsi di file di contenuto
    e viceversa, seguendo la convenzione page-bundle.

    La lingua di default viene servita senza prefisso nell'URL
    e corrisponde a file index.md. Le lingue non-default hanno
    un prefisso di esattamente 2 caratteri nell'URL e corrispondono
    a file index.<lingua>.md.

    Esempi:

        /chi-siamo        → CONTENT_DIR/chi-siamo/index.md
        /en/chi-siamo     → CONTENT_DIR/chi-siamo/index.en.md
        /                 → CONTENT_DIR/index.md
        /en/              → CONTENT_DIR/index.en.md
    """

    def __init__(self, cartella_base: Path | None = None) -> None:
        """
        Args:
            cartella_base (Path | None): Directory radice dei contenuti.
                Se non specificata, viene usato settings.CONTENT_DIR.
        """
        if cartella_base is None:
            cartella_base = settings.CONTENT_DIR
        
        self.base = cartella_base.resolve()
        self.alias = []


    def aggiungi_alias(self, cartella_alias: str, cartella_destinazione: str):
        """
        Aggiunge un alias all'elenco delle cartelle gestite.

        Esempio:
        aggiungi_alias("about-us", "chi-siamo")

        se successivamente richiamo Router.da_url("/en/about-us")
        mi deve restituire "{self.base}/chi-siamo/index.en.md"

        Args:
            cartella_alias (str): Nome della cartella (senza percorso)
                                     che deve fungere da alias
            cartella_destinazione (str): Nome della cartella (senza percorso)
                                         a cui va ridirezionato l'output
        """
        temp = {
            "alias": cartella_alias,
            "destinazione": cartella_destinazione,
        }
        self.alias.append(temp)


    def da_url(self, url: str) -> Path:
        """
        Converte un URL relativo nel percorso del file di contenuto
        corrispondente.

        Il primo segmento di 2 caratteri viene trattato come codice
        lingua (es. "en"); tutti gli altri URL vengono trattati come
        lingua di default (file index.md).

        Se il file calcolato esiste su disco viene restituito
        direttamente. Se non esiste, viene cercato un alias nei
        segmenti del path; in caso di corrispondenza si ritorna il
        percorso della cartella di destinazione dell'alias. Se non
        esiste né il file né un alias, viene sollevata FileNotFoundError.

        Non è possibile risalire fuori dalla cartella base tramite
        sequenze come `..`.

        Args:
            url (str): URL relativo, es. "/chi-siamo" o "/en/about-us".

        Returns:
            Path: Percorso assoluto del file di contenuto.

        Raises:
            ValueError: Se l'URL tenta di uscire dalla cartella base.
            FileNotFoundError: Se il file non esiste e non c'è nessun
                alias corrispondente.
        """
        url_clean = url.strip("/")

        if not url_clean:
            return self.base / "index.md"

        parti = url_clean.split("/")

        if len(parti[0]) == 2:
            lang = parti[0]
            segmenti_path = parti[1:]
            filename = f"index.{lang}.md"
        else:
            lang = None
            segmenti_path = parti
            filename = "index.md"

        target = self.base.joinpath(*segmenti_path, filename)

        try:
            target.resolve().relative_to(self.base)
        except ValueError:
            raise ValueError(
                f"Il percorso esce dalla cartella base: {url!r}"
            )

        if target.exists():
            return target

        alias_map = {a["alias"]: a["destinazione"] for a in self.alias}
        destinazione = alias_map.get("/".join(segmenti_path))
        if destinazione is not None:
            return self.base / destinazione / filename

        raise FileNotFoundError(
            f"File non trovato e nessun alias corrispondente: {url!r}"
        )


    def verso_url(self, percorso: Path) -> str:
        """
        Converte il percorso di un file di contenuto nell'URL
        corrispondente.

        Supporta due convenzioni di nome file:

        - index.md → lingua di default, URL senza prefisso lingua
        - index.<lingua>.md → lingua prefissata, URL con /<lingua>/

        Esempi:

            CONTENT_DIR/chi-siamo/index.md    → /chi-siamo/
            CONTENT_DIR/chi-siamo/index.en.md → /en/chi-siamo/
            CONTENT_DIR/index.md              → /
            CONTENT_DIR/index.en.md           → /en/

        Args:
            percorso (Path): Percorso del file di contenuto.

        Returns:
            str: URL relativo con slash iniziale (e finale tranne
                per la homepage della lingua di default).

        Raises:
            ValueError: Se il file non segue le convenzioni attese
                o non è dentro la cartella base.
        """
        percorso_risolto = percorso.resolve()

        try:
            relativo = percorso_risolto.relative_to(self.base)
        except ValueError:
            raise ValueError(
                f"Il percorso non è dentro la cartella base: {percorso!r}"
            )

        nome = relativo.name
        dir_relativa = relativo.parent
        dir_parts = [p for p in dir_relativa.parts if p != "."]

        if nome == "index.md":
            segmenti = dir_parts
        else:
            parti_nome = nome.split(".")
            if (
                len(parti_nome) != 3
                or parti_nome[0] != "index"
                or parti_nome[2] != "md"
            ):
                raise ValueError(
                    f"Il file non segue la convenzione index.md o "
                    f"index.<lingua>.md: {nome!r}"
                )
            lang = parti_nome[1]
            segmenti = [lang] + dir_parts

        if not segmenti:
            return "/"

        return "/" + "/".join(segmenti) + "/"


    def register(self, app: object) -> None:
        """
        Registra il Router nei global di Jinja2 dell'app Flask.

        Dopo la chiamata, nei template è disponibile `router`
        come variabile globale:

            {{ router.verso_url(percorso) }}
            {{ router.da_url('/chi-siamo') }}

        Args:
            app (object): Istanza dell'applicazione Flask.
        """
        app.jinja_env.globals["router"] = self
