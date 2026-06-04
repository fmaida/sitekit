from pathlib import Path

import frontmatter

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


    def _leggi_template(self, percorso: Path, default: str = "single.html") -> str:
        """
        Legge il campo template dal frontmatter del file di contenuto.

        Se il campo non è presente (o il file non esiste) restituisce
        il valore di default. Se il valore trovato non termina con
        ".html", l'estensione viene aggiunta automaticamente.

        Args:
            percorso (Path): Percorso del file .md da leggere.
            default (str): Template da usare se il campo non è presente.
                Default: "single.html".

        Returns:
            str: Il nome del template con estensione .html garantita.
        """
        if not percorso.exists():
            return default

        post = frontmatter.load(percorso)
        template = post.get("template", default)

        if not template.endswith(".html"):
            template = template + ".html"

        return template


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


    def da_url(self, url: str) -> tuple[Path, str]:
        """
        Converte un URL relativo nel percorso del file di contenuto
        corrispondente e nel nome del template da usare per renderizzarlo.

        Il primo segmento di 2 caratteri viene trattato come codice
        lingua (es. "en"); tutti gli altri URL vengono trattati come
        lingua di default.

        L'ordine di ricerca del file è:
        1. index.md / index.<lingua>.md
        2. _index.md / _index.<lingua>.md
        3. alias registrati via aggiungi_alias()

        Non è possibile risalire fuori dalla cartella base tramite
        sequenze come `..`.

        Args:
            url (str): URL relativo, es. "/chi-siamo" o "/en/about-us".

        Returns:
            tuple[Path, str]: Percorso assoluto del file di contenuto
                e nome del template letto dal campo "template" nel
                frontmatter. La stringa è vuota se il campo non esiste.

        Raises:
            ValueError: Se l'URL tenta di uscire dalla cartella base.
            FileNotFoundError: Se il file non esiste e non c'è nessun
                alias corrispondente.
        """
        url_clean = url.strip("/")
        default_template = "home.html" if not url_clean else "single.html"

        if not url_clean:
            segmenti_path = []
            lang = None
        else:
            parti = url_clean.split("/")
            if len(parti[0]) == 2:
                lang = parti[0]
                segmenti_path = parti[1:]
            else:
                lang = None
                segmenti_path = parti

        filename = f"index.{lang}.md" if lang else "index.md"
        alt_filename = f"_index.{lang}.md" if lang else "_index.md"

        target = self.base.joinpath(*segmenti_path, filename)

        try:
            target.resolve().relative_to(self.base)
        except ValueError:
            raise ValueError(
                f"Il percorso esce dalla cartella base: {url!r}"
            )

        if target.exists():
            return target, self._leggi_template(target, default_template)

        alt_target = self.base.joinpath(*segmenti_path, alt_filename)
        if alt_target.exists():
            return alt_target, self._leggi_template(alt_target, default_template)

        alias_map = {a["alias"]: a["destinazione"] for a in self.alias}
        destinazione = alias_map.get("/".join(segmenti_path))
        if destinazione is not None:
            percorso_alias = self.base / destinazione / filename
            if not percorso_alias.exists():
                percorso_alias = self.base / destinazione / alt_filename
            return percorso_alias, self._leggi_template(percorso_alias, default_template)

        raise FileNotFoundError(
            f"File non trovato e nessun alias corrispondente: {url!r}"
        )


    def verso_url(self, percorso: Path) -> str:
        """
        Converte il percorso di un file di contenuto nell'URL
        corrispondente.

        Supporta le varianti index e _index, con e senza suffisso lingua:

        - index.md / _index.md → lingua di default, URL senza prefisso
        - index.<lingua>.md / _index.<lingua>.md → URL con /<lingua>/

        Esempi:

            CONTENT_DIR/chi-siamo/index.md     → /chi-siamo/
            CONTENT_DIR/chi-siamo/_index.md    → /chi-siamo/
            CONTENT_DIR/chi-siamo/index.en.md  → /en/chi-siamo/
            CONTENT_DIR/chi-siamo/_index.en.md → /en/chi-siamo/
            CONTENT_DIR/index.md               → /
            CONTENT_DIR/index.en.md            → /en/

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

        if nome in ("index.md", "_index.md"):
            segmenti = dir_parts
        else:
            parti_nome = nome.split(".")
            if (
                len(parti_nome) != 3
                or parti_nome[0] not in ("index", "_index")
                or parti_nome[2] != "md"
            ):
                raise ValueError(
                    f"Il file non segue la convenzione index.md, "
                    f"_index.md, index.<lingua>.md o "
                    f"_index.<lingua>.md: {nome!r}"
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