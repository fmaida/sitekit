CACHE = {}
memoria_occupata = 0
memoria_massima = 4194304  # 4Mb al massimo

def carica(chiave: str) -> dict | None:
    return CACHE.get(chiave)

def salva(chiave: str, valore: object) -> bool:
    global memoria_occupata
    global memoria_massima

    if (memoria_occupata + len(valore)) < memoria_massima:
        CACHE[chiave] = valore
        memoria_occupata += len(valore)
        return True
    else:
        return False