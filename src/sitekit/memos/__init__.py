# v1.0 – 26/03/2026

from pathlib import Path
import datetime
import requests
import textwrap


class Config:
    def __init__(self, base_url: str, token: str | Path):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = token  # chiama il setter

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, valore: str | Path):
        if isinstance(valore, Path):
            valore = valore.read_text(encoding="utf-8").strip()
        self._token = valore
        self.session.headers.update({"Authorization": f"Bearer {valore}"})

        
# ––– Parametri globali –––
#CONFIG = Config(base_url="https://example.com", token=Path(__file__).parent / "token")


def _estrai_titolo(content) -> str|None:
    prima_riga = content.split("\n")[0].strip()
    if prima_riga.startswith("#"):
        return prima_riga.lstrip("#").strip()
    return None


def _converti_data(stringa) -> datetime.datetime:
    return datetime.datetime.strptime(stringa, "%Y-%m-%dT%H:%M:%SZ")
    

def _restituisci_allegati(memo) -> tuple[list, str]:
    """
    Restituisce una lista di stringhe contenenti gli URL
    agli allegati di una singola nota 
    """

    lista = []
    cover_image = None
    for allegato in memo["attachments"]:
        url = f"{CONFIG.base_url}/file/{allegato['name']}/{allegato['filename']}"
        lista.append(url)
        if allegato["type"].lower() in ["image/jpeg", "image/png", "image/gif", "image/webp", "image/avif", "image/svg+xml"]:
            if not cover_image:
                # Non c'era un immagine di copertina prima. La assegna
                cover_image = url
            else:
                # Era già stata scelta un'immagine di copertina
                # Se l'utente ci tiene a fare un override della
                # copertina, aggiunge la sottostringa "thumb_"
                # all'inizio del nome file, e il programma lo
                # accontenta.
                if allegato['filename'].startswith("thumb_"):
                    cover_image = url
        
        
    return lista, cover_image


def get(limit: int = 6) -> list[dict]:
    """
    Elenca tutte le note di un server Memos
    """
        
    # da qui in poi tutte le chiamate includono automaticamente il token
    response = CONFIG.session.get(f"{CONFIG.base_url}/api/v1/memos?pageSize={limit}")
    if response.status_code == 200:
        # print(json.dumps(response.json(), indent=2))
        dati = response.json()
        output = []
        for memo in dati["memos"]:
            allegati, image = _restituisci_allegati(memo)
            temp = {}
            temp["display_time"] = _converti_data(memo["displayTime"])
            temp["create_time"] = _converti_data(memo["createTime"])
            temp["update_time"] = _converti_data(memo["updateTime"])
            temp["title"] = _estrai_titolo(memo["content"])
            temp["content"] = memo["content"]
            temp["attachments"] = allegati
            temp["image"] = image
            output.append(temp)

        # Riordina i memo in ordine cronologico inverso
        output.sort(key=lambda x: x["display_time"], reverse=True)

        return output
    else:
        raise RuntimeError(f"Errore dal server: {response.status_code}")

def test(dati: list[dict]) -> None:
    for memo in dati:
        data = memo["display_time"].strftime("%d/%m/%Y %H:%M")
        troncato = textwrap.shorten(memo["content"], width=60, placeholder="...")
        titolo = memo["title"] if memo["title"] else troncato
        print(f"[{data}]  {titolo}")
        if memo["attachments"]:
            print("  contiene:")
            for allegato in memo["attachments"]:
                print(f"    – {allegato}")
        else:
            print("  (senza allegati)")
        if memo["image"]:
            print(f"  image:")
            print(f"    – {memo['image']}")


if __name__ == "__main__":
    dati = get()
    test(dati)