from pathlib import Path

from sitekit.settings import settings


# Un segmento di esattamente 2 caratteri è un codice lingua,
# uno di 3 o più è una chiave di sezione.
LUNGHEZZA_LINGUA = 2
LUNGHEZZA_SEZIONE_MINIMA = 3

_ESTENSIONI = ("md", "markdown")


def _analizza_nome(
    nome: str,
    stem: str,
    lingua_cartella: str | None = None,
) -> tuple[list[str], str]:
    """
    Scompone il nome di un file nei segmenti di sezione e nella lingua.

    La convenzione è `<stem>[.<sezione>]*[.<lingua>].md`, dove i
    segmenti si classificano per lunghezza: 2 caratteri esatti sono
    un codice lingua (ammesso solo come ultimo segmento), 3 o più
    sono una chiave di sezione annidabile.

    Esempi (con stem "index"):

        index.md                    → ([], lingua di default)
        index.intro.md              → (["intro"], lingua di default)
        index.history.gallery.md    → (["history", "gallery"], default)
        index.intro.en.md           → (["intro"], "en")

    Args:
        nome: nome del file, estensione compresa.
        stem: stem dell'indice del bundle ("index" o "_index").
        lingua_cartella: codice lingua ereditato dalla cartella che
            contiene il file, se si tratta di una cartella-lingua.

    Returns:
        Tupla con la lista dei segmenti di sezione (già minuscoli) e
        il codice lingua.

    Raises:
        ValueError: se il nome non segue la convenzione, se un
            segmento di sezione è troppo corto, o se dentro una
            cartella-lingua il nome porta comunque un suffisso lingua.
    """

    parti = nome.split(".")

    if len(parti) < 2 or parti[-1].lower() not in _ESTENSIONI:
        raise ValueError(f"Non è un file markdown: {nome!r}")

    if parti[0] != stem:
        raise ValueError(
            f"Il file non appartiene all'indice {stem!r}: {nome!r}"
        )

    segmenti = parti[1:-1]
    lingua = lingua_cartella or settings.DEFAULT_LANGUAGE

    if segmenti and len(segmenti[-1]) == LUNGHEZZA_LINGUA:
        if lingua_cartella:
            raise ValueError(
                f"Suffisso lingua {segmenti[-1]!r} dentro la "
                f"cartella-lingua {lingua_cartella!r}: {nome!r}"
            )
        lingua = segmenti.pop().lower()

    for segmento in segmenti:
        if len(segmento) < LUNGHEZZA_SEZIONE_MINIMA:
            raise ValueError(
                f"Il segmento {segmento!r} è troppo corto per essere "
                f"una sezione (minimo {LUNGHEZZA_SEZIONE_MINIMA} "
                f"caratteri): {nome!r}"
            )

    return [s.lower() for s in segmenti], lingua


def _appartiene(nome: str, stem: str) -> bool:
    """
    Dice se un nome di file fa parte dell'indice indicato.

    Args:
        nome: nome del file, estensione compresa.
        stem: stem dell'indice del bundle ("index" o "_index").

    Returns:
        True se il file condivide lo stem ed è un markdown.
    """

    parti = nome.split(".")

    return (
        len(parti) >= 2
        and parti[0] == stem
        and parti[-1].lower() in _ESTENSIONI
    )


def _raccogli_file(
    cartella: Path,
    stem: str,
) -> list[tuple[Path, str | None]]:
    """
    Elenca i file che compongono una pagina, in ordine di merge.

    Prima i file nella root del bundle (ordine alfabetico), poi
    quelli dentro le cartelle-lingua, cioè le sottocartelle con nome
    di esattamente 2 caratteri. Le altre sottocartelle (bundle figli,
    cartelle di asset) vengono ignorate.

    L'ordine determina la precedenza: a parità di chiave vince
    l'ultimo file, quindi la cartella-lingua ha la meglio sul file
    con suffisso lingua.

    Args:
        cartella: root del page bundle.
        stem: stem dell'indice del bundle ("index" o "_index").

    Returns:
        Lista di tuple (percorso, codice lingua della cartella). Il
        secondo elemento è None per i file nella root del bundle.
    """

    file_trovati: list[tuple[Path, str | None]] = []

    for percorso in sorted(cartella.glob("*")):
        if percorso.is_file() and _appartiene(percorso.name, stem):
            file_trovati.append((percorso, None))

    for sottocartella in sorted(cartella.glob("*")):
        if not sottocartella.is_dir():
            continue
        if len(sottocartella.name) != LUNGHEZZA_LINGUA:
            continue
        for percorso in sorted(sottocartella.glob("*")):
            if percorso.is_file() and _appartiene(percorso.name, stem):
                file_trovati.append((percorso, sottocartella.name.lower()))

    return file_trovati
