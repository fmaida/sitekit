# v1.0 - 10/10/2025
import json
from urllib.parse import urljoin
from . import schema, menu

out = {}

def clear(type_: str = "Restaurant"):
    global out
    out = schema.new(type_=type_)

    return out


def import_(data: dict):
    global out

    out = clear(type_=data.get("type") or "Restaurant")
    if out.get("type") == "Restaurant":
        out["hasMenu"] = menu.new()
        if data["menu"]:
            for dish in data["menu"]:
                menu.add_dish(name=dish.get("description"), description=None, image=dish.get("image"), price=dish.get("price"))
    out["name"] = data["title"]
    out["address"]["streetAddress"] = data["address"]["street"]
    out["address"]["addressLocality"] = data["address"]["locality"] or "Venice"

def add_product(data: dict):
    global out

    if out["type"] == "Restaurant":
        out["hasMenu"][""].append(menu.add_dish(data))


def generate():
    global out

    return f'''
    <script type=\"application/ld+json\">
    {json.dumps(out, ensure_ascii=False, indent=2)}
    </script>
    '''