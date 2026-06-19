import re

import markdown

from sitekit.settings import settings
from .attributi import analizza_attributi


# Forme accoppiate: aprono con il nome e chiudono con "end".
# Il gruppo 1 è il nome, il 2 gli attributi, il 3 il contenuto.
# La lookbehind (?<!/) esclude i tag auto-chiusi (".../>}}"),
# così non vengono scambiati per l'apertura di una coppia.
_ANGOLO_COPPIA = re.compile(
    r"\{\{<\s*(?!end\b)([\w-]+)([^>]*?)(?<!/)>\}\}(.*?)\{\{<\s*end\s*>\}\}",
    re.DOTALL,
)
_PERCENTO_COPPIA = re.compile(
    r"\{\{%\s*(?!end\b)([\w-]+)([^%]*?)(?<!/)%\}\}(.*?)\{\{%\s*end\s*%\}\}",
    re.DOTALL,
)

# Forme auto-chiuse: il marcatore "/" finale evita il tag "end".
_ANGOLO_SINGOLO = re.compile(r"\{\{<\s*(?!end\b)([\w-]+)([^>]*?)/>\}\}")
_PERCENTO_SINGOLO = re.compile(r"\{\{%\s*(?!end\b)([\w-]+)([^%]*?)/%\}\}")


class ProcessoreShortcode:
    """
    Espande shortcode in stile Hugo nel testo Markdown grezzo.

    Riconosce due delimitatori: {{< ... >}} passa il contenuto
    interno così com'è, mentre {{% ... %}} lo converte prima da
    Markdown a HTML. Ogni delimitatore esiste in forma accoppiata
    chiusa da un tag "end" e in forma auto-chiusa con il
    marcatore "/" finale (".../>}}" o ".../%}}"), che non
    richiede "end". Ogni shortcode viene reso dal template Jinja2
    omonimo presente in PLUGINS_DIR.
    """

    def __init__(self) -> None:
        try:
            from jinja2 import Environment, FileSystemLoader
        except ImportError as errore:
            raise ImportError(
                "Jinja2 è necessario per rendere gli shortcode ma "
                "non è installato nel virtualenv corrente."
            ) from errore

        self._ambiente = Environment(
            loader=FileSystemLoader(str(settings.PLUGINS_DIR)),
            autoescape=False,
        )


    def processa(self, content_raw: str) -> str:
        """
        Sostituisce tutti gli shortcode con l'HTML renderizzato.

        Le forme accoppiate vengono elaborate prima di quelle
        singole, così che un tag di apertura di una coppia non
        venga scambiato per uno shortcode singolo.

        Args:
            content_raw: testo Markdown grezzo con gli shortcode.

        Returns:
            Testo con gli shortcode espansi in HTML.
        """

        testo = _PERCENTO_COPPIA.sub(self._su_coppia_percento, content_raw)
        testo = _ANGOLO_COPPIA.sub(self._su_coppia_angolo, testo)
        testo = _ANGOLO_SINGOLO.sub(self._su_singolo, testo)
        testo = _PERCENTO_SINGOLO.sub(self._su_singolo, testo)

        return testo


    def _su_coppia_percento(self, match: re.Match) -> str:
        """
        Gestisce {{% nome %}}...{{% end %}} convertendo il
        contenuto interno da Markdown.
        """

        nome = match.group(1)
        attributi = analizza_attributi(match.group(2))
        contenuto = markdown.markdown(match.group(3).strip())

        return self._rendi(nome, attributi, contenuto, match.group(0))


    def _su_coppia_angolo(self, match: re.Match) -> str:
        """
        Gestisce {{< nome >}}...{{< end >}} passando il contenuto
        interno senza conversione Markdown.
        """

        nome = match.group(1)
        attributi = analizza_attributi(match.group(2))
        contenuto = match.group(3).strip()

        return self._rendi(nome, attributi, contenuto, match.group(0))


    def _su_singolo(self, match: re.Match) -> str:
        """
        Gestisce gli shortcode auto-chiusi (".../>}}" o
        ".../%}}"), senza contenuto interno e senza tag "end".
        """

        nome = match.group(1)
        attributi = analizza_attributi(match.group(2))

        return self._rendi(nome, attributi, "", match.group(0))


    def _rendi(
        self,
        nome: str,
        attributi: dict[str, str],
        contenuto: str,
        originale: str,
    ) -> str:
        """
        Renderizza il template del plugin con attributi e
        contenuto.

        Se il template non esiste lo shortcode viene lasciato
        invariato, così un refuso non interrompe la build.

        Args:
            nome: nome dello shortcode e del template Jinja2.
            attributi: coppie chiave/valore passate al template.
            contenuto: testo interno disponibile come "content".
            originale: testo originale dello shortcode, usato
                come fallback se il template manca.

        Returns:
            HTML renderizzato dal template, oppure il testo
            originale dello shortcode.
        """

        from jinja2 import TemplateNotFound

        try:
            template = self._ambiente.get_template(f"{nome}.jinja2")
        except TemplateNotFound:
            return originale

        variabili = dict(attributi)
        variabili["content"] = contenuto
        html = template.render(**variabili)

        return html
