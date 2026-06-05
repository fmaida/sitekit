# Sitekit

Libreria Python "coltellino svizzero" pensata per essere usata come dipendenza in generatori di siti statici basati su Flask + Frozen-Flask. Non è un generatore autonomo: fornisce moduli riutilizzabili da collegare a un progetto Flask.

## Stack e tooling

- **Python** ≥ 3.12, gestione dipendenze con **Poetry**
- **Test**: pytest (`poetry run pytest` dalla root)
- Il progetto usa `src/` layout: i sorgenti stanno in `src/sitekit/`

## Settings (`settings.py`)

Singleton `settings` (istanza di `SettingsClass`) disponibile ovunque via
`from sitekit.settings import settings`.

Tutte le path si basano su `BASE_DIR`, che viene auto-rilevato risalendo
l'albero di directory fino a trovare `pyproject.toml`. Non va mai impostato
a mano. L'unica proprietà che il progetto consumatore deve configurare
esplicitamente è `BASE_URL`.

| Proprietà | Default | Significato |
|---|---|---|
| `BASE_DIR` | auto (via pyproject.toml) | Root del progetto |
| `BASE_URL` | `https://example.com` | URL pubblico del sito |
| `CACHE_DIR` | `BASE_DIR / .cache` | Cache pickle e imagesdb |
| `CONTENT_DIR` | `BASE_DIR / content` | File markdown/yaml/json dei contenuti |
| `BUILD_DIR` | `BASE_DIR / build` | Output del freeze |
| `I18N_DIR` | `BASE_DIR / i18n` | File JSON di traduzione |
| `STATIC_DIR` | `BASE_DIR / static` | Asset statici |
| `TEMPLATES_DIR` | `BASE_DIR / templates` | Template Jinja2 |
| `PLUGINS_DIR` | `TEMPLATES_DIR / plugins` | Template Jinja2 dei plugin/shortcode |
| `SITE_LANGUAGES` | auto da I18N_DIR | Lista di tuple `(codice, nome)` |

## Moduli

### `images`

Converte e ridimensiona un'immagine sorgente in 4 breakpoint (400, 800, 1200, 1600px) nei formati AVIF, WebP e JPEG. Il breakpoint 1600px mantiene sempre l'aspect ratio originale; gli altri rispettano il parametro `aspect_ratio`.

```python
from sitekit import images
picture = images.copy(
    source_image=Path("content/hero.jpg"),
    destination_folder=Path("static/images"),
    aspect_ratio="16:9",   # default: "unchanged"
    anchor="top",          # "top" | "middle" | "bottom", default "middle"
    alt="Descrizione SEO", # default: stringa vuota
)
# picture è un PictureClass; str(picture) restituisce il tag <picture> HTML
```

**Caching a due livelli:**
1. `imgcache` (disco) — `imagesdb.json` in `CACHE_DIR`. Chiave:
   `(sha1, longest_side, output_folder, aspect_ratio, anchor)`. Include
   verifica che i file fisici esistano su disco.
2. Cache RAM — tiene in memoria l'ultimo file PIL aperto per evitare
   letture ripetute dello stesso sorgente.

`imgcache.salva()` va chiamato esplicitamente a fine build per persistere il db su disco. In `boilerplate-flask/tools/build.py` viene già fatto.

**`PictureClass`** — il `__str__` genera il tag `<picture>` completo con
srcset per tutti e tre i formati e tutti i breakpoint. Il nome del file
viene ricavato automaticamente da `folder.name` (= stem dell'immagine
sorgente), quindi non va mai hardcoded.

### `cache`

Cache a due livelli per file di contenuto (JSON, YAML, Markdown+frontmatter).

```python
from sitekit import cache
dati = cache.load(Path("content/pagina.md"))
# dati è un dict con le chiavi del frontmatter +
# "content_raw" (markdown grezzo, placeholder inclusi) e
# "content" (HTML renderizzato con plugin già iniettati)
```

Livello 1 — RAM (dict in memoria, azzerato a ogni riavvio del processo).
Livello 2 — Pickle su disco in `CACHE_DIR`, con chiave SHA1 del file
sorgente. Per i file markdown con plugin la chiave include anche l'mtime
dei template usati: modificare un template invalida automaticamente la
cache delle pagine che lo usano.

`cache.clean()` va chiamato a fine build per rimuovere i pickle dei file
non più usati nella run corrente.

#### Plugin / shortcode nei file markdown

I plugin si dichiarano nel frontmatter e si posizionano nel body con un
placeholder. La sintassi è:

```markdown
---
title: Titolo della pagina
plugins:
    - galleria:
          sorgente: "images/galleria1"
    - galleria:
          sorgente: "images/galleria2"
---

Prima galleria: {{< galleria >}}

Seconda galleria: {{< galleria >}}
```

I placeholder vengono abbinati ai plugin **in ordine posizionale per
tipo**: il primo `{{< galleria >}}` nel body usa i parametri del primo
`galleria` nel frontmatter, il secondo usa il secondo, e così via.

I template dei plugin sono file Jinja2 in `PLUGINS_DIR`
(`TEMPLATES_DIR / plugins`). Il template riceve i parametri dichiarati
nel frontmatter come variabili Jinja2:

```
templates/plugins/galleria.jinja2
```

Se un template dichiarato nel frontmatter non esiste su disco,
`cache.load` solleva `FileNotFoundError`. Se Jinja2 non è installato
nel virtualenv, solleva `ImportError`.

La sostituzione avviene **prima** del rendering markdown, così il markup
prodotto dal template non viene alterato dal renderer.

### `router`

Risolve URL multilingua in percorsi di file di contenuto e viceversa,
seguendo la convenzione page-bundle. La lingua di default è servita
senza prefisso; le lingue non-default hanno un prefisso di 2 caratteri.

```python
from sitekit.router import Router

router = Router()                          # usa settings.CONTENT_DIR
router = Router(cartella_base=Path("...")) # cartella personalizzata

# URL → file + template
percorso, template = router.da_url("/chi-siamo")
# /chi-siamo       → CONTENT_DIR/chi-siamo/index.md,    "single.html"
# /en/chi-siamo    → CONTENT_DIR/chi-siamo/index.en.md, "single.html"
# /                → CONTENT_DIR/index.md,               "home.html"

# file → URL
url = router.verso_url(Path("content/chi-siamo/index.en.md"))
# → "/en/chi-siamo/"

# alias (es. URL inglese che punta a cartella italiana)
router.aggiungi_alias("about-us", "chi-siamo")

# registrazione nei global Jinja2 di Flask
router.register(app)   # rende `router` disponibile nei template
```

**Ordine di ricerca file** per `da_url`: prima `index.md` (o
`index.<lingua>.md`), poi `_index.md` (o `_index.<lingua>.md`),
infine gli alias registrati.

**Template**: il nome viene letto dal campo `template` nel frontmatter
del file trovato; se assente usa `home.html` per la homepage o
`single.html` per le altre pagine. L'estensione `.html` viene aggiunta
automaticamente se mancante.

Solleva `ValueError` se l'URL tenta di uscire dalla cartella base
(traversal via `..`), `FileNotFoundError` se nessun file o alias
corrisponde all'URL.

### `shortcuts.content` e `shortcuts.i18n`

Wrapper di `cache.load` che prefissano rispettivamente `CONTENT_DIR` e `I18N_DIR`.

```python
from sitekit import content, i18n
dati = content.load("pagina.md")        # CONTENT_DIR / pagina.md
traduzioni = i18n.load("it.json")       # I18N_DIR / it.json
```

### `sitemap`

Genera `sitemap.xml` con supporto hreflang per siti multilingua.

```python
from sitekit import sitemap
sitemap.add("/it/chi-siamo/", alternate_url="/en/about/", locale="en")
sitemap.generate()  # scrive BUILD_DIR/sitemap.xml
```

`priority` viene assegnata automaticamente (1.0 per homepage, 0.5 per le altre)
se non specificata.

### `robots`

Genera `robots.txt`. Aggiunge automaticamente le direttive `Sitemap:` se trova
`sitemap.xml` o file `sitemap-*.xml` in `BUILD_DIR`.

```python
from sitekit import robots
robots.generate()  # scrive BUILD_DIR/robots.txt
```

### `localize`

Carica le stringhe di traduzione da un file JSON in `I18N_DIR` e aggiunge
i nomi dei giorni della settimana localizzati via Babel.

```python
from sitekit import localizza_stringhe
t = localizza_stringhe("it")  # fallback su "en" se la lingua non esiste
```

### `openings`

Modella gli orari di apertura di un'attività commerciale con supporto per
turni (`Turn`), giorni (`DayOpening`), festività (`Holiday`, `HolidayList`)
e la classe contenitore `Openings`.

### `jsonld`

Genera strutture JSON-LD (schema.org) per menu e schemi generici da iniettare
nel `<head>` delle pagine.

### `rssreader`

Wrapper attorno a `feedparser`. Allo stato attuale ha implementazioni minimali
in `wordpress.py` e `memos.py`. Da completare quando necessario.

## Convenzioni sui test

I test stanno in `tests/`. Ogni modulo ha il suo file `test_<modulo>.py`.
Le fixture usano `tmp_path` di pytest per l'isolamento su disco.
I globali di modulo (`imgcache.CACHE`, `images.ultima_immagine`) vengono
resettati esplicitamente nelle fixture `autouse` per evitare interferenze
tra test.

Il comando per lanciare i test è `pytest` dalla root del progetto.

## Metadata
- Ultima modifica: 2026-06-05
- Modello: claude-sonnet-4-6


