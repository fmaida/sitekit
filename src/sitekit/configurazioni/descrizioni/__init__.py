from sitekit.settings import CONTENT_DIR
import yaml
import markdown
import re
from sitekit import cache


def elenca(sito: str) -> list[str]:
    """
    Restituisce un elenco delle lingue per cui esiste
    una descrizione del ristorante.
    """
    
    cartella = CONTENT_DIR / sito / "descriptions"

    if cartella.exists() and cartella.is_dir():
        return [f.stem for f in cartella.iterdir() if f.is_file() and f.suffix == ".md"]
    else:
        return []
    
def esiste(sito: str, lingua: str) -> bool:
    """
    Controlla se esiste una descrizione per il ristorante
    nella lingua specificata.
    """

    cartella = CONTENT_DIR / sito / "descriptions"
    
    file_descrizione = cartella / (lingua + ".md")
    return file_descrizione.exists() and file_descrizione.is_file()

def carica(sito, lingua) -> tuple[str | None, str]:
    """
    Carica la descrizione del ristorante, 
    se presente in una sottocartella chiamata
    'descriptions'
    """

    descrizione = ""

    file_descrizione = CONTENT_DIR / sito / "descriptions" / (lingua + ".md")

    if file_descrizione.exists():
        descrizione = cache.load(file_descrizione)["content_raw"].strip()
        #with open(file_descrizione, 'r', encoding='utf-8') as f:
        #    descrizione = f.read().strip()
        titolo, descrizione = _estrai_e_rimuovi_titolo(descrizione)            
    else:
        titolo, descrizione = None, carica_fallback(sito, lingua)
    
    return titolo, markdown.markdown(descrizione)

def carica_fallback(sito, lingua):
    """
    Carica le descrizioni del ristorante, se 
    presente in un file descriptions.yaml. E 
    poi restituisce quella nella lingua in
    cui stiamo attualmente lavorando.
    """
    
    descrizione = []
    
    # Percorso assoluto o relativo al file
    cartella = CONTENT_DIR / sito / "descriptions.yaml"
    
    # Se il file esiste lo carica
    if cartella.exists():
        data = cache.load(cartella)
        #with open(cartella, 'r', encoding='utf-8') as f:            
        #    data = yaml.safe_load(f)
        
        # Prende la descrizione nella lingua in
        # cui stiamo lavorando. Se non c'è una
        # descrizione nella lingua in cui 
        # lavoriamo, per fallback prende quella 
        # in lingua inglese
        descrizione = data[lingua] if lingua in data else data.get("en", "[No Description]")
    
    return descrizione

def _estrai_e_rimuovi_titolo(descrizione):
    """
    Estrae la prima sottostringa che inizia con # e termina con \n,
    la restituisce e la elimina da temp.
    """
    match = re.search(r'#.*?\n', descrizione)
    titolo = match.group(0).replace("#", "").strip() if match else None
    if titolo:
        descrizione = descrizione.replace(titolo, '', 1).strip()
    return titolo, descrizione

def salva(sito, lingua, testo):
    """
    Salva la descrizione del ristorante in un file
    """
    cartella = CONTENT_DIR / sito / "descriptions"
    cartella.mkdir(parents=True, exist_ok=True)

    file_descrizione = cartella / (lingua + ".md")    
    with open(file_descrizione, 'w', encoding='utf-8') as f:
        f.write(testo)
    