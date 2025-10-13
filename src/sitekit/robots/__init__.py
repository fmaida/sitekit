# v1.0 - 10/10/2025
from sitekit.settings import settings


def generate():
    # Crea robots.txt ottimizzato per l'indicizzazione
    robots_lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /*/r/",  # pagina interna per richieste recensioni
    ]

    # Se esiste un file sitemap.xml lo aggiunge
    if settings.BUILD_DIR.exists() and (settings.BUILD_DIR / "sitemap.xml").exists():
        robots_lines.append(f"Sitemap: {settings.BASE_URL}/sitemap.xml")

    # Aggiunge eventuali sitemap paginated (es: sitemap-1.xml) se presenti
    for sm in sorted(settings.BUILD_DIR.glob("sitemap-*.xml")):
        robots_lines.append(f"Sitemap: {settings.BASE_URL}/{sm.name}")

    # Scrittura file robots.txt senza Path.write_text
    if not settings.BUILD_DIR.exists():
        settings.BUILD_DIR.mkdir(parents=True)
    robots_path = settings.BUILD_DIR / "robots.txt"
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write("\n".join(robots_lines))
        f.write("\n")