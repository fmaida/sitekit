# v1.1 - 10/10/2025
from datetime import datetime
from urllib.parse import urljoin
from xml.sax.saxutils import escape
from sitekit.settings import settings


url_list = []

def add(url: str, alternate_url: str = None, locale: str = None, change_freq: str = "monthly", priority: float = None):
    global url_list

    if priority is None:
        homepage_variants = {"", "/", "index.html", "/index.html"}
        priority = 1.0 if url in homepage_variants else 0.5

    abs_path = urljoin(settings.BASE_URL + "/", url)
    if locale:
        # Trova il dizionario nella lista di
        # url_list che contiene come chiave "url"
        # il valore del parametro url
        # Trova il dizionario principale corrispondente all'URL
        found = False
        for link in url_list:
            if link["url"] == urljoin(settings.BASE_URL + "/", url):
                link["locale"].append({"url": urljoin(settings.BASE_URL + "/", alternate_url), "locale": locale})
                found = True
                break
        if not found:
            #if "demo/en/privacy" in link["url"]:
            #    breakpoint()
            # Se non trovato, lo crea e aggiunge subito
            # la variante locale
            url_list.append({
                "url": urljoin(settings.BASE_URL + "/", url),
                "locale": [{"url": urljoin(settings.BASE_URL + "/", alternate_url), "locale": locale}],
                "change_freq": change_freq,
                "priority": priority
            })
        # Nel dizionario trovato, appendi alla lista
        # indicata nella chiave "locale" un nuovo
        # dizionario con chiave "url" = url e "locale" = locale

    else:
        # Aggiunge la versione base senza locale
        url_list.append({"url": urljoin(settings.BASE_URL + "/", url),
                         "locale": [],
                         "change_freq": change_freq,
                         "priority": priority})

def generate():
    today = datetime.now().strftime("%Y-%m-%d")

    with open(settings.BUILD_DIR / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        f.write("<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"\n")
        f.write("        xmlns:xhtml=\"http://www.w3.org/1999/xhtml\">\n")
        for link in url_list:
            f.write(f"  <url>\n")
            f.write(f"    <loc>{escape(link["url"])}</loc>\n")
            if link["locale"]:
                for locale in link["locale"]:
                    f.write(f"    <xhtml:link rel=\"alternate\" hreflang=\"{locale['locale']}\" href=\"{escape(locale['url'])}\"/>\n")
            f.write(f"    <lastmod>{today}</lastmod>\n")
            f.write(f"    <changefreq>{link["change_freq"]}</changefreq>\n")
            f.write(f"    <priority>{link["priority"]}</priority>\n")
            f.write(f"  </url>\n")
        f.write("</urlset>\n")