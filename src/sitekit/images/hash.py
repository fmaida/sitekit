from hashlib import md5, sha1
from pathlib import Path


# Calcola l'SHA-1 di un file
# MD5 anche se vecchiotto e non sicuro, basta 
# e avanza per calcolare più velocemente di 
# SHA-1 e SHA-256 se un file è stato 
# modificato oppure no
def _calcola_sha1(percorso: Path) -> str | None:
    if not percorso.exists():
        return None
    
    h = sha1() #md5()
    with open(percorso, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    
    # Restituisce l'SHA-1
    return h.hexdigest()