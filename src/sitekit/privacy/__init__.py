import frontmatter
import markdown
from sitekit.settings import LOCALE_DIR


def esiste(lingua: str) -> bool:
    """
    Indica se la privacy policy nella lingua
    indicata esiste sul disco
    """

    privacy_dir = LOCALE_DIR / "privacy"
    return (privacy_dir / (lingua + ".md")).exists()

def carica(lingua: str, params: dict = {}) -> dict | None:
    privacy_dir = LOCALE_DIR / "privacy"

    try:
        temp = frontmatter.load(privacy_dir / (lingua + ".md"), encoding="UTF-8")
    except FileNotFoundError:
        # Lingua di fallback
        temp = frontmatter.load(privacy_dir / "en.md", encoding="UTF-8")
    if params.get("title"):
        temp.content = temp.content.replace("{{ params.title }}", params.get("company_name", params.get("title")))
    if params.get("address"):
        temp.content = temp.content.replace("{{ params.address }}", params["address"]["street"] + ", " + params["address"]["postal_code"] + " " + params["address"]["locality"])
    if params.get("email"):
        temp.content = temp.content.replace("{{ params.email }}", params["email"])
    if params.get("phone"):
        temp.content = temp.content.replace("{{ params.phone }}", params["phone"])
    params["content"] = markdown.markdown(temp.content)
    return params

def salva(lingua: str, testo: str) -> None:
    """
    Salva la privacy policy per la lingua 
    indicata sul disco
    """
    
    privacy_dir = LOCALE_DIR / "privacy"
    
    with open(privacy_dir / (lingua + ".md"), "w", encoding="UTF-8") as f:
        f.write(testo)