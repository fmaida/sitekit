def _carica_temi(params):

    if "settings" not in params:
        params["settings"] = {}
    if "theme" not in params["settings"]:
        params["settings"]["theme"] = "light"

    # Imposta i colori per il tema chiaro
    # (a meno che non ci abbia già pensato il 
    # file yaml del ristorante)

    if "light" not in params["settings"]:
        params["settings"]["light"] = {}
    
    params["settings"]["light"].setdefault("background", "#fff")
    params["settings"]["light"].setdefault("color", "#1a1a1f")
    params["settings"]["light"].setdefault("accent", "#b34930")
    params["settings"]["light"].setdefault("bar", "#e3e0e0")
    params["settings"]["light"].setdefault("disabled", "#977F44")
    
    # Imposta i colori per il tema scuro
    # (a meno che non ci abbia già pensato il 
    # file yaml del ristorante)
    if "dark" not in params["settings"]:
        params["settings"]["dark"] = {}
    params["settings"]["dark"].setdefault("background", "#222")
    params["settings"]["dark"].setdefault("color", "#eee")
    params["settings"]["dark"].setdefault("accent", "#C6B280")
    params["settings"]["dark"].setdefault("bar", "#1a1a1f")
    params["settings"]["dark"].setdefault("disabled", "#6c757d")

    return params