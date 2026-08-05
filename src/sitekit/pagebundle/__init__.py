from datetime import datetime
from pathlib import Path

from sitekit.settings import settings
from . import media
from .asset import _ancora_asset
from .lettura import _carica_valore
from .nomi import _analizza_nome, _raccogli_file
from .normalizza import _normalizza_contenuti
from .unione import _annida, _deep_merge


# Ordine di ricerca dell'indice dentro un page bundle.
_NOMI_INDICE = ("index.md", "_index.md")


def load(percorso: str | Path, copia_asset: bool = True) -> dict:
    """
    Carica un page bundle, cioè una pagina e i suoi asset.

    Una pagina può stare tutta in un file solo oppure essere spezzata
    su più file secondo la convenzione
    `<stem>[.<sezione>]*[.<lingua>].md`: i segmenti di 3 o più
    caratteri sono chiavi di sezione annidabili, quello finale di
    esattamente 2 caratteri è un codice lingua. Le due forme
    producono lo stesso identico dizionario.

    Esempi (con stem "index"):

        index.md                    → radice
        index.intro.md              → dati["intro"]
        index.history.gallery.md    → dati["history"]["gallery"]
        index.intro.en.md           → dati["localization"]["en"]["intro"]

    Le sottocartelle con nome di 2 caratteri sono cartelle-lingua ed
    equivalgono al suffisso lingua sul nome file: `en/index.intro.md`
    vale quanto `index.intro.en.md`.

    Gli asset della cartella vengono convertiti e copiati sotto
    `assets/`, e i riferimenti relativi nel markdown vengono
    riscritti di conseguenza.

    Args:
        percorso: cartella del page bundle, oppure percorso esplicito
            del file indice.
        copia_asset: se False non tocca il disco e non riscrive i
            riferimenti. Utile quando servono solo i dati.

    Returns:
        Dict con il frontmatter di tutti i file fusi insieme, più
        "slug" (nome del bundle), "content"/"content_raw" a ogni
        livello che ha del testo, "localization" con le lingue
        diverse da settings.DEFAULT_LANGUAGE, e — se presenti —
        "date" e "cover".

    Raises:
        FileNotFoundError: se il percorso non esiste o la cartella non
            contiene né index.md né _index.md.
        ValueError: se un nome di file non segue la convenzione.
    """

    percorso = Path(percorso)

    if percorso.is_dir():
        cartella = percorso
        indice = next(
            (cartella / nome for nome in _NOMI_INDICE if (cartella / nome).is_file()),
            None,
        )
        if indice is None:
            raise FileNotFoundError(f"Index not found on \"{cartella}\".")
    elif percorso.is_file():
        indice = percorso
        cartella = percorso.parent
    else:
        raise FileNotFoundError(f"File non trovato: \"{percorso}\"")

    stem = indice.name.split(".")[0]
    slug = _slug_bundle(cartella)

    gruppi: dict[str, dict] = {}
    for segmenti, lingua, valore in _voci(cartella, stem):
        if not segmenti and not isinstance(valore, dict):
            raise ValueError(
                f"L'indice della pagina non può avere un frontmatter "
                f"a sequenza: \"{cartella}\""
            )
        gruppi[lingua] = _deep_merge(
            gruppi.get(lingua, {}),
            _annida(segmenti, valore),
        )

    dati = gruppi.pop(settings.DEFAULT_LANGUAGE, {})
    if gruppi:
        dati["localization"] = {
            lingua: gruppi[lingua] for lingua in sorted(gruppi)
        }

    dati.setdefault("slug", slug)
    slug = dati["slug"]

    if dati.get("date"):
        dati["date"] = _normalizza_data(dati["date"])

    if copia_asset:
        cover = media.copia(cartella, slug)
        if cover:
            dati["cover"] = cover

    dati = _normalizza_contenuti(dati)

    if copia_asset:
        dati = _ancora_asset(dati, slug, cartella)

    return dati


# I page bundle caricati come singola pagina si chiamavano così
# prima che il modulo imparasse a leggere anche le sezioni.
load_single = load


def load_collection(path: Path) -> list[dict]:
    """
    Carica tutti i page bundle di una cartella, ordinati per data.

    Serve per blog e news, dove ogni sottocartella è un post. Le
    pagine senza `date` nel frontmatter la ricavano dalla data di
    creazione della cartella, così l'ordinamento è sempre possibile.

    Args:
        path: cartella che contiene i page bundle.

    Returns:
        Lista di dizionari come quelli di `load`, dal più vecchio al
        più recente.
    """

    pagine = []

    for elemento in sorted(Path(path).glob("*")):
        if not elemento.is_dir():
            continue

        dati = load(elemento)
        if not dati.get("date"):
            creazione = datetime.fromtimestamp(elemento.stat().st_ctime)
            dati["date"] = creazione.strftime("%Y-%m-%d")

        pagine.append(dati)

    return sorted(pagine, key=lambda pagina: pagina["date"])


def localizzato(dati: dict, lingua: str) -> dict:
    """
    Restituisce la pagina nella lingua richiesta, con fallback.

    La radice (lingua di default) viene fusa con
    `dati["localization"][lingua]`: le chiavi tradotte vincono, le
    altre restano nella lingua di default invece di sparire.

    Args:
        dati: dizionario prodotto da `load`.
        lingua: codice della lingua desiderata.

    Returns:
        Un nuovo dizionario senza la chiave "localization".
    """

    base = {
        chiave: valore
        for chiave, valore in dati.items()
        if chiave != "localization"
    }

    traduzione = (dati.get("localization") or {}).get(lingua)
    if not traduzione:
        return base

    return _deep_merge(base, traduzione)


def _normalizza_data(valore) -> str:
    """
    Riduce una data a stringa YYYY-MM-DD.

    Args:
        valore: date, datetime o stringa dal frontmatter.

    Returns:
        La data in formato ISO breve, o il valore originale se non è
        una data.
    """

    try:
        return valore.strftime("%Y-%m-%d")
    except AttributeError:
        return valore


def _slug_bundle(cartella: Path) -> str:
    """
    Ricava il nome della pagina dalla cartella che la contiene.

    Il file si chiama `index.md`, ma il nome vero della pagina è
    quello del page bundle: `pagina/index.md` è la pagina "pagina".
    Nella root di CONTENT_DIR non c'è nessun bundle, quindi lo slug
    è vuoto.

    Args:
        cartella: cartella che contiene il file indice.

    Returns:
        Nome della cartella, o stringa vuota se è la root dei
        contenuti.
    """

    if cartella.resolve() == settings.CONTENT_DIR.resolve():
        return ""

    return cartella.name


def _voci(cartella: Path, stem: str):
    """
    Produce i pezzi della pagina già nell'ordine di merge.

    L'indice viene prima delle sezioni (così un file di sezione
    sovrascrive la chiave omonima dichiarata inline nel frontmatter
    dell'indice) e i file con suffisso lingua vengono prima delle
    cartelle-lingua.

    Args:
        cartella: root del page bundle.
        stem: stem dell'indice ("index" o "_index").

    Yields:
        Tuple (segmenti di sezione, codice lingua, valore caricato).
    """

    voci = []
    for posizione, (file, lingua_cartella) in enumerate(
        _raccogli_file(cartella, stem)
    ):
        segmenti, lingua = _analizza_nome(file.name, stem, lingua_cartella)
        gruppo = 0 if lingua_cartella is None else 1
        voci.append((gruppo, len(segmenti), posizione, segmenti, lingua, file))

    voci.sort(key=lambda voce: voce[:3])

    for _, _, _, segmenti, lingua, file in voci:
        yield segmenti, lingua, _carica_valore(file)
