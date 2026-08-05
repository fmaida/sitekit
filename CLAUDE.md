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
| `STATIC_CONTENT` | `/static` | Prefisso URL con cui gli asset statici vengono serviti |
| `TEMPLATES_DIR` | `BASE_DIR / templates` | Template Jinja2 |
| `PLUGINS_DIR` | `TEMPLATES_DIR / plugins` | Template Jinja2 dei plugin/shortcode |
| `SITE_LANGUAGES` | auto da I18N_DIR | Lista di tuple `(codice, nome)` |
| `SITE_LANGUAGE_CODES` | derivata | Solo i codici di `SITE_LANGUAGES` |
| `SITE_LANGUAGE_NAMES` | derivata | Solo i nomi di `SITE_LANGUAGES` |
| `DEFAULT_LANGUAGE` | `it` | Lingua servita senza prefisso né suffisso |
| `BUNDLE_ASSETS_URL` | `cache/{slug}` | Cartella (dentro static) degli asset di un page bundle |
| `VERBOSE` | `False` | Abilita l'output diagnostico |

`STATIC_DIR` e `STATIC_CONTENT` non sono la stessa cosa e vanno tenute
allineate a mano: la prima è la cartella su disco in cui vengono scritti
gli asset, la seconda è il prefisso URL con cui il server li espone (usato
dal filtro `static` degli shortcode).

**`I18N_DIR` va cambiata solo con `settings.set_i18n_dir(percorso)`**, mai
assegnando l'attributo: il metodo ricalcola `SITE_LANGUAGES`,
`SITE_LANGUAGE_CODES` e `SITE_LANGUAGE_NAMES` leggendo i file JSON della
nuova cartella. Un'assegnazione diretta lascia le tre liste ferme sui
valori vecchi.

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

`imgcache.clean()` va chiamato a fine build per rimuovere da `imagesdb.json` le entry orfane (immagini eliminate o non più referenziate nei contenuti). Chiama `salva()` internamente, quindi sostituisce `imgcache.salva()` quando si vuole anche la pulizia.

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

`cache.prune(days=60)` cancella da `CACHE_DIR` tutti i file più vecchi di
N giorni. Serve alle applicazioni long-running, dove `clean()` non basta
perché la cartella accumula pickle di run precedenti. **Non viene invocata
automaticamente**: va chiamata esplicitamente all'avvio dell'applicazione.

Il modulo, all'import, si limita a creare `CACHE_DIR` se non esiste.

#### Shortcode: due meccanismi distinti

Esistono due modi di iniettare HTML generato da template Jinja2 dentro un
markdown, e **convivono**. `cache.load` li applica entrambi e include i
template di entrambi nel digest della cache.

1. **Plugin dichiarati nel frontmatter** — descritti qui sotto. Parametri
   nel frontmatter, placeholder nel body, abbinamento posizionale.
2. **Shortcode in stile Hugo** — attributi inline nel body, nessuna
   dichiarazione nel frontmatter. Vedi la sezione [`shortcodes`](#shortcodes).

Il secondo è più recente ed espressivo; il primo resta per i contenuti che
lo usano già. Per contenuti nuovi preferire gli shortcode Hugo.

#### Plugin dichiarati nel frontmatter

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

### `shortcodes`

Espande shortcode in stile Hugo scritti direttamente nel body markdown,
senza dichiararli nel frontmatter. Gli attributi si scrivono inline e
finiscono nel template come variabili Jinja2.

```python
from sitekit import shortcodes
html = shortcodes.renderizza(content_raw)
```

Normalmente non va chiamato a mano: `cache.load` lo invoca già su ogni
file markdown.

**Due delimitatori**, che si comportano diversamente sul contenuto interno:

| Sintassi | Contenuto interno |
|---|---|
| `{{< nome >}}...{{< end >}}` | passato al template così com'è |
| `{{% nome %}}...{{% end %}}` | convertito da Markdown a HTML prima di passarlo |

Ognuno esiste anche in **forma auto-chiusa**, con un `/` finale che rende
superfluo il tag `end`: `{{< nome />}}` e `{{% nome /%}}`.

```markdown
{{< galleria sorgente="images/galleria1" />}}

{{% riquadro titolo="Nota" %}}
Questo testo **viene** convertito da markdown.
{{% end %}}
```

Il template riceve gli attributi come variabili e il contenuto interno
nella variabile riservata `content`:

```jinja2
{# templates/plugins/riquadro.jinja2 #}
<aside><h3>{{ titolo }}</h3>{{ content }}</aside>
```

I template stanno in `PLUGINS_DIR`, come per i plugin del frontmatter, e
si chiamano `<nome>.jinja2`. Nel template è disponibile il filtro globale
`static()`, che prefissa un percorso con `STATIC_CONTENT` lasciando
invariati gli URL assoluti (`http://`, `https://`, `//`):

```jinja2
<img src="{{ static('/images/foto/foto__800.jpg') }}">
{# → /static/images/foto/foto__800.jpg #}
```

**Template mancante**: a differenza dei plugin del frontmatter, che
sollevano `FileNotFoundError`, uno shortcode il cui template non esiste
viene lasciato **invariato** nel testo. Un refuso non interrompe la build,
ma non se ne accorge nessuno: comparirà il testo grezzo dello shortcode
nella pagina. Se Jinja2 non è installato, `ProcessoreShortcode.__init__`
solleva `ImportError`.

Le forme accoppiate vengono elaborate prima di quelle auto-chiuse, così un
tag di apertura non viene scambiato per uno shortcode singolo. `autoescape`
è **disattivato**: i template producono HTML grezzo e sono responsabili
del proprio escaping.

`shortcodes.percorsi_template(file)` restituisce i template usati dagli
shortcode di un file. Serve alla cache: includendoli nel digest, la chiave
cambia quando uno di essi viene modificato. I template inesistenti vengono
ignorati, coerentemente con il rendering tollerante.

### `pagina`

Carica una pagina composta da **uno o più** file frontmatter+markdown.
Una pagina lunga può stare tutta in un file solo oppure essere spezzata
in file separati: le due forme producono lo **stesso identico dizionario**.

```python
from sitekit import pagina

dati = pagina.load(Path("content/chi-siamo"))           # page bundle
dati = pagina.load(Path("content/chi-siamo/index.md"))  # file indice esplicito

titolo_italiano = dati["title"]
titolo_inglese = dati["localization"]["en"]["title"]

# radice fusa con la traduzione: le chiavi non tradotte non spariscono
inglese = pagina.localizzato(dati, "en")
```

**Convenzione di naming**: `<stem>[.<sezione>]*[.<lingua>].md`, dove
`<stem>` è `index` o `_index`. I segmenti si classificano per lunghezza:
3 caratteri o più sono chiavi di sezione annidabili, esattamente 2 sono
un codice lingua (ammesso solo come ultimo segmento). Un segmento di 1
carattere solleva `ValueError`.

```
index.md                     → radice, lingua di default
index.intro.md               → dati["intro"]
index.history.gallery.md     → dati["history"]["gallery"]
index.en.md                  → dati["localization"]["en"]
index.history.gallery.en.md  → dati["localization"]["en"]["history"]["gallery"]
```

Quindi questo file singolo:

```markdown
---
title: Titolo
subsection:
    title: Titolo della sottosezione
    content: Questo è il contenuto della sottosezione
---

Questo è il contenuto principale
```

equivale a `index.md` + `index.subsection.md`, dove il corpo di ciascun
file diventa il `content` della sua sezione. `content` è un **nome
riservato**: si può usare nel frontmatter, ma qualsiasi corpo markdown
lo sovrascrive.

**Merge**: l'indice viene applicato per primo, poi le sezioni; a parità
di chiave vince il file di sezione sul frontmatter inline dell'indice.
Le mappe vengono fuse in profondità, le liste sostituite. Se il
frontmatter di un file di sezione è una **sequenza** YAML anziché una
mappa, il valore della sezione *è* quella lista (un corpo markdown non
vuoto in quel caso solleva `ValueError`).

**`content` / `content_raw`**: come in `cache`, ogni sezione con del
testo espone il markdown grezzo in `content_raw` e l'HTML in `content`.
La normalizzazione è ricorsiva e vale anche per un `content:` scritto
inline nel frontmatter — è ciò che rende equivalenti le due forme. Le
sezioni senza testo non portano nessuna delle due chiavi.

#### Page bundle

Il file si chiama `index.md`, ma il nome vero della pagina è quello
della cartella: `chi-siamo/index.md` è la pagina `chi-siamo`. Finisce in
`dati["slug"]`, che è vuoto nella root di `CONTENT_DIR` (homepage) e
viene sovrascritto da uno `slug:` presente nel frontmatter.

Una **sottocartella con nome di esattamente 2 caratteri** è una
cartella-lingua, equivalente al suffisso lingua sul nome file:

```
pagina/                          ≡   pagina/
    index.md                             index.md
    index.intro.md                       index.intro.md
    en/                                  index.en.md
        index.md                         index.intro.en.md
        index.intro.md
```

Dentro una cartella-lingua i nomi file non portano il suffisso lingua
(`en/index.fr.md` solleva `ValueError`). Le sottocartelle con nome di 3+
caratteri (bundle figli, cartelle di asset) vengono ignorate.

**Asset relativi**: un riferimento relativo nel markdown punta sempre
alla root del page bundle, anche quando il file che lo contiene sta in
una cartella-lingua. Dopo il rendering, gli `src`/`href` relativi
diventano URL assoluti sotto `BUNDLE_ASSETS_URL`:

```
![](foto.jpg)   →   <img src="/static/cache/<slug>/foto.jpg">
```

Restano invariati URL assoluti, percorsi che iniziano con `/`, ancore e
schemi come `mailto:`, insieme a `content_raw` e ai valori del
frontmatter. Attributi diversi da `src`/`href` (per esempio il
`data-src` di un template plugin) non vengono toccati.

### `pagebundle`

**Modulo precedente a `pagina`, da non confondere con la sottosezione
"Page bundle" qui sopra.** Carica un bundle come singolo file
(`_index.md`, con fallback su `index.md`) tramite `cache.load` e copia gli
asset della cartella nella destinazione statica. Non conosce i file di
sezione, le cartelle-lingua né `localization`.

```python
from sitekit import pagebundle

pagebundle.set_media_destination_folder(Path("static/cache"))
post  = pagebundle.load_single(Path("content/blog/primo-post"))
posts = pagebundle.load_collection(Path("content/blog"))  # ordinati per data
```

`load_single` aggiunge al dizionario:

- `slug` — nome della cartella
- `date` — dal frontmatter, normalizzata a `YYYY-MM-DD`; se assente, ricavata
  dalla data di creazione della cartella
- `cover` — stem del primo file immagine che contiene `_cover` nel nome

Gli asset vengono copiati in `MEDIA_DESTINATION_FOLDER / <nome cartella>`
(default `STATIC_DIR / cache`). Le immagini `.jpg`, `.jpeg` e `.png` passano
per `images.copy` con `aspect_ratio="4:3"` **fisso**; `.md`, `.yaml`, `.yml`
e `.json` vengono ignorati; tutto il resto viene copiato tal quale.

Per pagine nuove usare `pagina`, che copre gli stessi casi in modo più
generale. `pagebundle` resta per il codice che lo usa già, in particolare
per le collezioni ordinate per data (blog, news), che `pagina` non offre.

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

In `verso_url` il suffisso è un codice lingua solo se lungo esattamente
2 caratteri: i file di sezione di `pagina` (`index.intro.md`) non sono
pagine e sollevano `ValueError`.

### `shortcuts.content` e `shortcuts.i18n`

Wrapper di `cache.load` che prefissano rispettivamente `CONTENT_DIR` e `I18N_DIR`.

```python
from sitekit import content, i18n
dati = content.load("pagina.md")        # CONTENT_DIR / pagina.md
dati = content.load("blog", "post.md")  # CONTENT_DIR / blog / post.md
traduzioni = i18n.load("it.json")       # I18N_DIR / it.json
```

Entrambe accettano più segmenti di percorso. `content.load` accetta anche
istanze di `Path`: se ne riceve una **assoluta**, la usa direttamente senza
prefissare `CONTENT_DIR`.

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

### `privacy`

Legge e scrive la privacy policy, un file markdown per lingua in
`I18N_DIR / privacy / <lingua>.md`.

```python
from sitekit import privacy

privacy.esiste("it")                    # -> bool
dati = privacy.carica("it", params)     # params arricchito con "content" (HTML)
privacy.salva("it", testo_markdown)
```

`carica` fa fallback su `en.md` se la lingua richiesta non esiste, e
sostituisce nel testo alcuni segnaposto con i valori presi da `params`:

| Segnaposto | Origine in `params` |
|---|---|
| `{{ params.title }}` | `company_name`, con fallback su `title` |
| `{{ params.address }}` | `address` (`street`, `postal_code`, `locality`) |
| `{{ params.email }}` | `email` |
| `{{ params.phone }}` | `phone` |

Nonostante la sintassi, **non sono variabili Jinja2**: la sostituzione è una
`str.replace` letterale, e i quattro segnaposto sopra sono gli unici
riconosciuti. `carica` **muta e restituisce** il dizionario `params` che
riceve, aggiungendoci la chiave `content` con l'HTML. Il valore di default
del parametro è un dict mutabile condiviso fra le chiamate: passare sempre
un proprio dizionario.

Se `en.md` non esiste, il fallback solleva `FileNotFoundError`. `salva` non
crea la cartella `privacy/`: deve esistere già.

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

### `memos`

Client per l'API REST di un server [Memos](https://usememos.com), **distinto
da `rssreader.memos`**, che invece ne legge il feed RSS. Questo modulo parla
direttamente con `/api/v1/memos` via `requests` e richiede un token.

```python
from sitekit import memos

memos.set_base_url("https://memos.example.com")
memos.set_token(Path.home() / ".config" / "memos.token")  # str o Path
note = memos.get(limit=6)
```

`set_token` accetta una stringa oppure una `Path`, nel qual caso legge il
file e ne usa il contenuto. Il token viene messo nell'header
`Authorization` della sessione condivisa.

Vengono restituite solo le note **pubbliche**, in ordine cronologico
inverso. Ogni nota è un dict con `title` (dall'eventuale intestazione `#`
sulla prima riga), `content`, `tags` (gli hashtag nel testo),
`attachments` (URL), `image` (primo allegato immagine, o quello il cui
nome file inizia con `thumb_`), `url`, e i tre timestamp `display_time`,
`create_time`, `update_time` come `datetime`.

Due opzioni globali per i titoli: `always_force_a_title(True)` genera un
titolo troncando il contenuto quando la nota non ne ha uno,
`wrap_titles_at(n)` accorcia i titoli a `n` caratteri.

`memos.test(dati)` stampa le note a schermo, per uso diagnostico.

Se il server risponde con un codice diverso da 200, `get` solleva
`RuntimeError`.

### `configurazioni`

Carica la configurazione di un sito-ristorante da `CONTENT_DIR / <slug>`,
mettendo insieme scheda, descrizione, orari, menu, indicazioni, immagini
e tema in un unico dizionario pronto per il template.

```python
from sitekit import configurazioni

for cartella in configurazioni.elenca():   # generatore di Path
    params = configurazioni.carica(cartella.name, "it")

params = configurazioni.vuoto(slug="", lingua="en")  # minimo per non far crashare
```

`carica` legge `_index.md` (fallback `index.md`) più, se presenti,
`descriptions/`, `openings.yaml`, `menu.yaml` e `directions.yaml` nella
stessa cartella; converte tutte le immagini che vi trova; e aggiunge
`json-ld`, `base_url`, `slug`, `lang`, `accepted_languages` e i `<link
rel="alternate">` hreflang. Lingue fuori da `SITE_LANGUAGE_CODES` fanno
fallback su `en`. Se il frontmatter contiene `redirect`, il caricamento si
ferma lì e gli altri file non vengono letti.

C'è una **cache in RAM per `(sito, lingua)` con TTL di 12 ore**, separata da
quella di `cache`: `configurazioni.CACHE`. Un processo long-running non vede
le modifiche ai contenuti prima della scadenza; svuotare il dict a mano per
forzare il ricaricamento.

Il sottomodulo `configurazioni.descrizioni` gestisce i testi descrittivi per
lingua (`elenca`, `esiste`, `carica`, `carica_fallback`, `salva`).

> **Nota.** Questo modulo è codice di dominio ristorativo dentro una libreria
> altrimenti generica: assume `price`/`EUR`, orari di apertura e una struttura
> di cartelle specifica. Va trattato come API pubblica perché è riesportato da
> `sitekit/__init__.py`, ma non è un buon modello per i moduli nuovi.

## Convenzioni sui test

I test stanno in `tests/`, un file `test_<modulo>.py` per modulo. La
copertura è **parziale**: hanno test `cache`, `images`, `jsonld`,
`openings`, `pagina`, `robots`, `router`, `rssreader` e `shortcodes`
(`settings` sotto il nome `test_impostazioni.py`). Non ne hanno
`configurazioni`, `localize`, `memos`, `pagebundle`, `privacy`,
`shortcuts` e `sitemap`: toccando quei moduli, conviene aggiungerli.

Le fixture usano `tmp_path` di pytest per l'isolamento su disco.
I globali di modulo (`imgcache.CACHE`, `images.ultima_immagine`) vengono
resettati esplicitamente nelle fixture `autouse` per evitare interferenze
tra test.

Il comando per lanciare i test è `pytest` dalla root del progetto.

I file di esempio stanno in `tests/examples/`. Le tre cartelle in
`tests/examples/frontmatter+markdown/` (`esempio_unito`,
`esempio_separato`, `esempio_cartelle_lingua`) descrivono la stessa
pagina nelle tre forme accettate da `pagina.load` e devono restare
equivalenti: i test verificano che producano lo stesso dizionario.

## Metadata
- Ultima modifica: 2026-08-05
- Modello: claude-opus-5


