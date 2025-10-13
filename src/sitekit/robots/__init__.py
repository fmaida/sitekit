# v1.0 - 10/10/2025
from sitekit.settings import BASE_URL, BUILD_DIR


def generate():
    # Crea robots.txt ottimizzato per l'indicizzazione
    robots_lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /*/r/",  # pagina interna per richieste recensioni
        f"Sitemap: {BASE_URL}/sitemap.xml",
    ]
    # Aggiunge eventuali sitemap paginated (es: sitemap-1.xml) se presenti
    for sm in sorted(BUILD_DIR.glob("sitemap-*.xml")):
        robots_lines.append(f"Sitemap: {BASE_URL}/{sm.name}")

    # Scrittura file robots.txt senza Path.write_text
    robots_path = BUILD_DIR / "robots.txt"
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write("\n".join(robots_lines))
        f.write("\n")