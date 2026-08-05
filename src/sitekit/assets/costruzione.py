import shutil
from pathlib import Path

from sitekit.settings import settings
from .percorsi import cartella_generati


def _sorgenti() -> list[Path]:
    """
    Le cartelle che confluiscono in ASSETS_DIR, in ordine di merge.

    L'ordine determina la precedenza: a parità di percorso relativo
    vince l'ultima, cioè STATIC_DIR.

    Returns:
        Lista di Path: generati, resources, static.
    """

    return [
        cartella_generati(),
        settings.RESOURCES_DIR,
        settings.STATIC_DIR,
    ]


def build(pulisci: bool = False) -> int:
    """
    Unisce le sorgenti degli asset dentro ASSETS_DIR.

    Confluiscono, in quest'ordine, gli asset generati in
    CACHE_DIR/assets, i sorgenti da elaborare di RESOURCES_DIR e i
    sorgenti già pronti di STATIC_DIR. La struttura delle cartelle
    viene ricopiata tale e quale: `static/css/style.css` diventa
    `assets/css/style.css`.

    La copia è incrementale — un file viene riscritto solo se manca
    o se differisce per dimensione o data — quindi la funzione può
    essere richiamata a ogni avvio dell'applicazione a costo quasi
    nullo.

    Args:
        pulisci: se True rimuove da ASSETS_DIR i file che non
            provengono più da nessuna sorgente, e le cartelle
            rimaste vuote.

    Returns:
        Numero di file effettivamente copiati.
    """

    finale = settings.ASSETS_DIR
    finale.mkdir(parents=True, exist_ok=True)
    finale_risolta = finale.resolve()

    provenienza: dict[Path, Path] = {}
    copiati = 0

    for sorgente in _sorgenti():
        if not sorgente.is_dir():
            continue
        if sorgente.resolve() == finale_risolta:
            continue

        for file in sorted(sorgente.rglob("*")):
            if not file.is_file():
                continue
            if finale_risolta in file.resolve().parents:
                # La destinazione è annidata dentro una sorgente:
                # non si ricopia addosso a se stessa.
                continue

            relativo = file.relative_to(sorgente)

            if relativo in provenienza and settings.VERBOSE:
                print(
                    f"⚠️  Asset in conflitto: \"{relativo}\" viene da "
                    f"\"{provenienza[relativo]}\" e da \"{sorgente}\"; "
                    f"vince la seconda."
                )

            provenienza[relativo] = sorgente

            if _copia_se_serve(file, finale / relativo):
                copiati += 1

    if pulisci:
        _rimuovi_orfani(finale, set(provenienza))

    return copiati


def _copia_se_serve(origine: Path, destinazione: Path) -> bool:
    """
    Copia un file solo se la destinazione non è già aggiornata.

    `shutil.copy2` preserva la data di modifica, quindi un file già
    copiato e non più toccato ha esattamente la stessa mtime della
    sua origine e viene saltato.

    Args:
        origine: file sorgente.
        destinazione: percorso di destinazione.

    Returns:
        True se il file è stato copiato, False se era già a posto.
    """

    if destinazione.exists():
        stat_origine = origine.stat()
        stat_destinazione = destinazione.stat()
        if (
            stat_origine.st_size == stat_destinazione.st_size
            and stat_origine.st_mtime <= stat_destinazione.st_mtime
        ):
            return False

    destinazione.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origine, destinazione)

    return True


def _rimuovi_orfani(radice: Path, validi: set[Path]) -> None:
    """
    Cancella da ASSETS_DIR i file che nessuna sorgente produce più.

    Args:
        radice: ASSETS_DIR.
        validi: percorsi relativi visti durante l'unione.
    """

    for file in radice.rglob("*"):
        if file.is_file() and file.relative_to(radice) not in validi:
            try:
                file.unlink()
            except OSError:
                pass

    # Le cartelle si svuotano dall'interno verso l'esterno.
    for cartella in sorted(radice.rglob("*"), reverse=True):
        if cartella.is_dir() and not any(cartella.iterdir()):
            try:
                cartella.rmdir()
            except OSError:
                pass


def register(app: object, costruisci: bool = True) -> None:
    """
    Rende ASSETS_DIR raggiungibile dal server di prova.

    Se l'applicazione è già stata costruita puntando lo static
    folder ad ASSETS_DIR non serve nessuna route in più; altrimenti
    ne viene aggiunta una dedicata, così gli asset si vedono anche
    in sviluppo.

    Per il freeze conviene comunque costruire l'app così:

        app = Flask(__name__,
                    static_folder=settings.ASSETS_DIR,
                    static_url_path=settings.ASSETS_URL)

    perché Frozen-Flask copia da sé lo static folder, mentre una
    route con segnaposto `<path:>` non è scopribile da sola.

    Args:
        app: istanza dell'applicazione Flask.
        costruisci: se True chiama `build()` subito dopo.
    """

    prefisso = settings.ASSETS_URL.rstrip("/")

    if (getattr(app, "static_url_path", None) or "").rstrip("/") != prefisso:
        from flask import send_from_directory

        def _servi_asset(percorso: str):
            return send_from_directory(settings.ASSETS_DIR, percorso)

        app.add_url_rule(
            f"{prefisso}/<path:percorso>",
            "sitekit_assets",
            _servi_asset,
        )

    if costruisci:
        build()
