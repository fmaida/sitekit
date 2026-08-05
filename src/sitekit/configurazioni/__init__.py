import frontmatter
import yaml
from pathlib import Path
from datetime import datetime, timedelta

from babel.numbers import format_currency
from babel.dates import format_date
from .images import image_copier, marca_come_convertite
from sitekit import cache, jsonld
from .themes import _carica_temi
from sitekit.configurazioni import descrizioni
from sitekit import images
from sitekit.assets import percorsi as assets
from sitekit.settings import settings

# Questa variabile tiene in memoria
# i parametri di configurazione 
# dei ristoranti in base a ristorante 
# e alla lingua, per evitare di 
# caricarli continuamente dalla RAM
CACHE = {}


def elenca():
    """
    Elenca i ristoranti per i quali sono 
    disponibili configurazioni.
    """

    for sito in settings.CONTENT_DIR.iterdir():
        if sito.is_dir():
            if  (sito / "index.md").exists() or (sito / "_index.md").exists():
                yield sito

def vuoto(slug: str = "", lingua: str = "en") -> dict:
    """
    Restituisce un dict di configurazione
    'quasi vuoto', che però contiene il tema
    di default del sito

    Args:
        slug: Slug del ristorante
        lingua: Lingua da utilizzare

    Returns:
        dict: Un dizionario con i
                parametri di configurazione minimi
                per non far crashare il server
    """

    # Controlla le impostazioni dei colori
    params = _carica_temi({})
    params["slug"] = slug

    # Aggiunge le informazioni su quando la 
    # configurazione è stata generata
    temp = datetime.now()
    params["created_at"] = temp.isoformat()
    params["created_at_locale"] = format_date(temp, locale=lingua, format="long")
    
    return params

def carica(sito: str, lingua: str) -> dict:
    """
    Carica i parametri di configurazione del ristorante specificato.

    args:
        sito (str): Il codice del ristorante (es: "scla").
        lingua (str): La lingua in cui caricare i parametri (es: "it", "en").

    returns:
        dict: Un dizionario con i parametri del ristorante.
    """    
    global CACHE

    # Verifica che la lingua sia supportata
    if lingua not in settings.SITE_LANGUAGE_CODES:
        lingua = "en"

    # Prova a vedere se in memoria 
    # nella cache ha già caricato 
    # questa combinazione di sito + lingua
    cache_chiave = (sito, lingua)
    if cache_chiave in CACHE:
        # Ha trovato un valore nella cache
        # Verifica la validità della cache 
        # (non deve essere più vecchia di 12 ore)
        timestamp_str = CACHE[cache_chiave].get("timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
            if datetime.now() - timestamp <= timedelta(hours=12):
                # A posto. La cache è valida.
                # Restituisce il suo valore anziché
                # rigenerarlo.
                return CACHE[cache_chiave]
            else:
                # Invalida la cache
                del CACHE[cache_chiave]

    # Ok, niente da fare...
    # Non aveva già in cache una configurazione
    # consona per sito + lingua. Tocca generarla
    # a partire dai dati che ha sul disco
    

    params = _carica_scheda_ristorante(sito=sito,
                                       lingua=lingua)

    # Aggiunge i percorsi URL alle versioni 
    # alternative della pagina del ristorante
    params["pagina"] = {}
    params["pagina"]["versioni_alternative"] = []
    
    for selezione in settings.SITE_LANGUAGES:
        temp = f"<link rel=\"alternate\" hreflang=\"{selezione[0]}\" href=\"{settings.BASE_URL}/{sito}/{selezione[0]}/\" />"
        params["pagina"]["versioni_alternative"].append(temp)
    temp = f"<link rel=\"alternate\" hreflang=\"x-default\" href=\"{settings.BASE_URL}/{sito}/\" />"
    params["pagina"]["versioni_alternative"].append(temp)
    
    params["base_url"] = settings.BASE_URL
    params["slug"] = sito
    params["lang"] = lingua
    params["accepted_languages"] = settings.SITE_LANGUAGES
    
    # Verifica se deve fare un redirect
    # Se fa un redirect, non è necessario
    # caricare tutti gli altri file di
    # configurazione per il ristorante
    if not params.get("redirect"):

        # Non deve fare un redirect
    
        # Carica la descrizione del ristorante
        titolo, descrizione = descrizioni.carica(sito, lingua)
        params["content"] = descrizione
        if titolo:
            params["title"] = titolo

        # Carica gli orari di apertura del ristorante
        # (se disponibili in un file openings.yaml)
        openings = _carica_aperture(sito=sito, lingua=lingua)
        params["opening_hours"] = openings

        # Carica i piatti consigliati dallo chef
        # (se disponibili in un file menu.yaml)
        menu = _carica_piatti(sito=sito, lingua=lingua)
        params["menu"] = menu

        # Carica le indicazioni per raggiungere il
        # ristorante con i mezzi di trasporto pubblici
        # (se disponibili in un file directions.yaml)
        directions = _carica_indicazioni(sito=sito, lingua=lingua)
        params["indicazioni"] = directions
        
        # Controlla le impostazioni dei colori
        params = _carica_temi(params)

    # Aggiunge le informazioni su quando la 
    # configurazione è stata generata
    temp = datetime.now()
    params["created_at"] = temp.isoformat()
    params["created_at_locale"] = format_date(temp, locale=lingua, format="long")
    
    # Abbiamo terminato di creare il file di
    # configurazione per sito + lingua
    # Per evitare di doverlo rifare a breve,
    # salva la configurazione nella cache in RAM
    CACHE[cache_chiave] = params
    CACHE[cache_chiave]["timestamp"] = datetime.now().isoformat()

    # Crea uno script json-ld che poi potrà incorporare nella pagina html
    params["json-ld"] = jsonld.import_(params)

    # Restituisce la configurazione
    return params

def _carica_scheda_ristorante(sito, lingua) -> dict | None:
    """
    Carica la scheda principale del ristorante
    dalla cartella di configurazione, 
    solitamente si tratta di un file index.md o
    _index.md
    """
    
    temp = {}

    # Percorso assoluto o relativo al file
    cartella = settings.CONTENT_DIR / sito
    
    # Prova a caricare il file
    try:
        # Prova a caricare il file _index.md
        place = cache.load(cartella / "_index.md")
        #place = frontmatter.load(cartella / "_index.md")
    except FileNotFoundError:
        # Se non ci riesce, prova a caricare 
        # il file index.md 
        place = cache.load(cartella / "index.md")
        #place = frontmatter.load(cartella / "index.md")
    
    # Inserisce nel dizionario `temp` i metadati del file frontmatter+markdown
    temp.update(place)  # place.metadata)    

    # Verifica le immagini presenti nella cartella
    # in cui si trova il file di configurazione
    temp["images"] = _carica_immagini(sito=sito,
                                      cartella_immagini=cartella,
                                      cartella_destinazione=assets.destinazione(f"images/{sito}"))

    # Abbiamo convertito tutte le immagini. Il
    # processo di conversione è stato lunghino,
    # pertanto per risparmiarci tempo macchina
    # ci segnamo di avere già convertito queste
    # immagini in modo da non ripetere
    # l'operazione.

    # La funzione `image_copier` si andrà a
    # leggere questo marcatore ed eviterà di
    # rifare il lavoro nel caso
    marca_come_convertite(sito)

    # Alle eventuali immagini inserite nella galleria fotografica, che
    # nel file YAML contengono solo il nome del file, aggiungo il percorso
    # assoluto per accedere sul server. Es: /static/images/<codice>/<immagine>
    if "gallery" in temp:
        temp["gallery_path"] = []
        for i, image in enumerate(temp["gallery"]):
            percorso = f"images/{sito}/{Path(image).stem}/{Path(image).stem}"
            temp["gallery_path"].append(percorso)

    return temp

def _carica_immagini(sito: str, cartella_immagini: Path, cartella_destinazione: Path) -> list:
    """
    Scansiona la cartella che conteneva il
    file di configurazione (es: /content/<sito>)
    alla ricerca di immagini da convertire
    e le aggiunge alla lista image_files

    Args:
        sito: slug del ristorante
        cartella_immagini: La cartella da scansionare
        cartella_destinazione: La cartella in cui salvare le immagini

    Returns:
        list: Una lista di collegamenti alle immagini convertite
    """

    image_files = []

    for img_path in cartella_immagini.glob("*"):
        if img_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            # Se il file termina con un estensione
            # .jpg, .jpeg o .png lo converte,
            # aggiungendolo poi alla lista dei
            # file immagine convertiti
            #immagine = image_copier(folder_name=sito,
            #                        image_path=img_path)
            #image_files.append(immagine)
            images.copy(source_image=img_path, destination_folder=cartella_destinazione)
            temp = "images/" + sito + "/" + img_path.stem + "/" + img_path.stem
            image_files.append(temp)

    # Se il nome file di un immagine contiene la
    # sottostringa `_cover`, voglio che sia il
    # primo della lista. Così verrà sicuramente
    # utilizzato per creare l'immagine di copertina

    # Riordina le immagini trovate mettendo quelle
    # che contengono la sottostringa `_cover`
    # in alto. Così abbiamo sempre l'immagine di
    # copertina come prima immagine
    image_files.sort(key=lambda s: (0 if "_cover" in s else 1, s.lower()))

    return image_files

def _carica_piatti(sito: str, lingua: str) -> dict:
    """
    Carica un elenco di piatti consigliati dallo
    chef, qualora sia presente un file menu.yaml

    Args:
        sito: Slug del ristorante
        lingua: Lingua in cui estrarre i piatti

    Returns:
        dict: Un dizionario con i piatti
                raccomandati dallo chef
    """

    piatti = []
    # Percorso assoluto o relativo al file
    cartella = settings.CONTENT_DIR / sito / "menu.yaml"
    
    if cartella.exists():
        data = cache.load(cartella)
        #with open(cartella, 'r', encoding='utf-8') as f:            
        #    data = yaml.safe_load(f)
        
        # Per ogni piatto trovato nel file yaml
        for piatto in data:
            # Formatta il prezzo del piatto in base alla localizzazione
            if "price" in piatto:
                piatto["price_fmt"] = format_currency(piatto["price"], "EUR", locale=lingua)
            
            # Modifica il percorso all'immagine
            # inserendo quello corretto per il template
            if "image" in piatto:
                piatto["image_path"] = f"images/{sito}/" + Path(piatto["image"]).stem + "/" + Path(piatto["image"]).stem
            
            # Estrae la descrizione del piatto nella lingua
            # in cui stiamo attualmente lavorando. Se 
            # non abbiamo una descrizione nella lingua in
            # cui stiamo lavorando, per default usa l'italiano
            piatto["description"] = piatto.get(lingua, piatto.get("it"))
            piatti.append(piatto)
    
    return piatti

def _carica_aperture(sito: str, lingua: str) -> list:
    """
    Carica gli orari di apertura del ristorante,
    se è presente un file openings.yaml

    Args:
        sito: Slug del ristorante
        lingua: Lingua in cui estrarre gli orari

    Returns:
        list: Un elenco di dizionari con i giorni di apertura
    """

    aperture = []
    
    # Percorso assoluto o relativo al file
    file_aperture = settings.CONTENT_DIR / sito / "openings.yaml"
    
    # Se il file esiste
    if file_aperture.exists():
        data = cache.load(file_aperture)
        #with open(file_aperture, 'r', encoding='utf-8') as f: 
        #    data = yaml.safe_load(f)
        
        aperture = data
    
    return aperture

def _carica_indicazioni(sito: str, lingua: str) -> dict:
    """
    Carica le indicazioni per arrivare al
    ristorante, se un file directions.yaml è
    presente

    Args:
        sito: Slug del ristorante
        lingua: Lingua in cui estrarre le indicazioni

    Returns:
        list: Una lista di dizionari con le indicazioni
    """

    indicazioni = []
    
    # Percorso assoluto o relativo al file
    file_indicazioni = settings.CONTENT_DIR / sito / "directions.yaml"
    
    if file_indicazioni.exists():
        data = cache.load(file_indicazioni)
        #with open(file_indicazioni, 'r', encoding='utf-8') as f:            
        #    data = yaml.safe_load(f)
        
        indicazioni = data
    
    return indicazioni