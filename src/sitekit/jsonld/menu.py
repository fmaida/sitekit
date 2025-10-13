from pathlib import Path


out = {}

def new():
    global out

    out = {
        "@type": "MenuSection",
        "name": "",
        "hasMenuItem": [],
    }

    return out

def add_dish(name: str, description: str = None, image: Path = None, price: float = None):
    global out

    new_dish: dict[str, any] = {
        "@type": "MenuItem",
    }

    if name:
        new_dish["name"] = name
    if description:
        new_dish["description"] = description
    if image:
        new_dish["image"] = str(image)
    if price:
        new_dish["offers"] = {}
        new_dish["offers"] = {"@type": "Offer", "price": str(price), "priceCurrency": "EUR"}

    out["hasMenuItem"].append(new_dish)