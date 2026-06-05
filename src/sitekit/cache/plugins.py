import re
from collections import deque

from sitekit.settings import settings


def _renderizza_plugin(content_raw: str, plugins_raw: list) -> str:
    """
    Sostituisce i placeholder {{< nome >}} nel testo markdown
    con l'HTML renderizzato dal template Jinja2 corrispondente.

    I placeholder vengono abbinati ai plugin dichiarati nel
    frontmatter in ordine posizionale per tipo: il primo
    {{< galleria >}} usa i parametri del primo plugin galleria
    dichiarato, il secondo usa i parametri del secondo, e così
    via.

    Args:
        content_raw: testo markdown grezzo con i placeholder.
        plugins_raw: lista di dict dal frontmatter (chiave =
            nome plugin, valore = dict dei parametri).

    Returns:
        Testo markdown con i placeholder sostituiti dall'HTML
        dei template plugin renderizzati.

    Raises:
        ImportError: se Jinja2 non è installato nel virtualenv.
    """

    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        raise ImportError(
            "Jinja2 è necessario per rendere i plugin shortcode "
            "ma non è installato nel virtualenv corrente."
        )

    env = Environment(
        loader=FileSystemLoader(str(settings.PLUGINS_DIR)),
        autoescape=False,
    )

    queues: dict[str, deque] = {}
    for item in plugins_raw:
        if not isinstance(item, dict):
            continue
        for nome, params in item.items():
            if nome not in queues:
                queues[nome] = deque()
            queues[nome].append(params or {})

    def _sostituisci(match: re.Match) -> str:
        nome = match.group(1)
        if nome not in queues or not queues[nome]:
            return match.group(0)
        params = queues[nome].popleft()
        template = env.get_template(f"{nome}.jinja2")

        return template.render(**(params if isinstance(params, dict) else {}))

    return re.sub(r"\{\{<\s*(\w+)\s*>\}\}", _sostituisci, content_raw)
