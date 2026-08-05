# API Contract — `sitekit`

> **Documento generato automaticamente. Non modificarlo a mano.**
> Descrive la sola superficie pubblica del pacchetto: firme, tipi e
> docstring. Serve a un agente IA che lavora su un progetto *consumatore*
> di questa libreria e ha bisogno di conoscerne il contratto attuale.
>
> Per le convenzioni di sviluppo interne al pacchetto vedi `CLAUDE.md`.


## Verifica di validita'

Prima di fidarti di questo documento, esegui il controllo di deriva:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/generate_contract.py" \
    . --check
```

Se un modulo risulta *disallineato*, il documento non descrive piu' il codice: leggi il sorgente di quel modulo e rigenera il contratto.
Un `api_sha256` invariato con `file_sha256` diverso significa che sono cambiati solo dettagli interni: il contratto pubblico regge.

## Indice dei moduli

| Modulo | api_sha256 | file_sha256 |
| --- | --- | --- |
| `sitekit` | `1aef9256b064c15c` | `cd3ff431472608ad` |
| `sitekit.assets` | `d3ad19ff54239ab2` | `c4d61aca7690d5d6` |
| `sitekit.assets.costruzione` | `c92240c66cc40a60` | `4cc4c77e6ae47794` |
| `sitekit.assets.percorsi` | `37ca1b03ac5ce093` | `ecaa704dae38a965` |
| `sitekit.cache` | `890d690ab049c52f` | `2748c075de5a0f4f` |
| `sitekit.cache.ram` | `8dc87f5117648857` | `c82c90b05fa8639b` |
| `sitekit.configurazioni` | `c7fe2c8f4dc284fa` | `bdcc259194b43785` |
| `sitekit.configurazioni.descrizioni` | `8c58c8968a20f3fb` | `96127530152bbd5f` |
| `sitekit.configurazioni.images` | `0297c7887d76b9fe` | `9e7780f9a3ffad7e` |
| `sitekit.configurazioni.imgcache` | `c78e2fd7167a97fc` | `7b6b8003f9406ef0` |
| `sitekit.images` | `ff059c280cabeb4f` | `5cdc4a1519353747` |
| `sitekit.images.images` | `339a9ab3dd98e357` | `df67bdedf40248ee` |
| `sitekit.images.imgcache` | `3b1eb946b805471b` | `a1c2509c1e6196c8` |
| `sitekit.images.picture_class` | `4b843e3658dd066c` | `5805d29f409e8e41` |
| `sitekit.jsonld` | `784d114313fb8136` | `bb5a79bdb003cb84` |
| `sitekit.jsonld.menu` | `350b90329c6f6197` | `49dc5e601b317d1b` |
| `sitekit.jsonld.schema` | `31da952caea594d9` | `7be792788c843cf5` |
| `sitekit.localize` | `a32940845b92d7eb` | `56f9d6bef586bc80` |
| `sitekit.memos` | `ae17689cb565bc44` | `c36135e2015b2dbb` |
| `sitekit.openings` | `7a20a6de024cdf52` | `b944a053cd564cef` |
| `sitekit.openings.classes` | `2c578d3e3e6a5b11` | `fbd99057d62e8886` |
| `sitekit.openings.classes.dayopeningclass` | `c5a5dca11da2544d` | `090067fd8bcca0fd` |
| `sitekit.openings.classes.holidayclass` | `0687d659b9203922` | `b732b48e7f386c3b` |
| `sitekit.openings.classes.holidaylistclass` | `1a68890633ca457f` | `70fc78fe9cf08598` |
| `sitekit.openings.classes.openingsclass` | `060ba3bb731602bc` | `9a80b0c3f86a3c5d` |
| `sitekit.openings.classes.turnclass` | `d50276826b9e56f3` | `fab77eb109a9df6b` |
| `sitekit.pagebundle` | `99ac4ba347e5dc2a` | `6ae67749faebfe23` |
| `sitekit.pagebundle.media` | `cd33d814895402cf` | `aee22b9851608606` |
| `sitekit.pagebundle.nomi` | `c14ced8cd6d72b63` | `252f281fd8de6299` |
| `sitekit.privacy` | `3e5f924d5f5befb1` | `af823c1378e492d4` |
| `sitekit.robots` | `cf7d1fd7a07641b3` | `50eb4436aa177c05` |
| `sitekit.router` | `6800513c8678a343` | `233c645b8dfdd3df` |
| `sitekit.router.router` | `87c4c604f79efe70` | `3ae9dc97904713e3` |
| `sitekit.rssreader` | `20a734ed3ebb18c9` | `d45dc361af653458` |
| `sitekit.rssreader.memos` | `92e3f95d9be5198b` | `d1ee4150e4915f99` |
| `sitekit.rssreader.wordpress` | `502127c44ce28ed4` | `38c0367a69247d49` |
| `sitekit.settings` | `9b4ff52367ed1de0` | `f5b07ff3c6158017` |
| `sitekit.shortcodes` | `06cd0408d47dd823` | `9a19f0e32b965672` |
| `sitekit.shortcodes.attributi` | `65543927f106a695` | `f9c5a46620670eae` |
| `sitekit.shortcodes.filtri` | `42b86ed821e4f5ec` | `dc606b89e6332d87` |
| `sitekit.shortcodes.processore` | `9e166bd4274475f5` | `fdbef6ee32cc3b61` |
| `sitekit.shortcodes.scoperta` | `bfbdc276f62ab315` | `cc9483893757eb57` |
| `sitekit.shortcuts` | `fd445c07308830e6` | `33426ee6e70b8a89` |
| `sitekit.shortcuts.content` | `aa7eaf3e360b17a1` | `1a748770b4f5fb08` |
| `sitekit.shortcuts.i18n` | `ad546bd986c68c2f` | `1ba2acde9cf2d440` |
| `sitekit.sitemap` | `a43e39cf265cbf8f` | `0c36b37a0d3ef1d1` |

## `sitekit`

File: `src/sitekit/__init__.py`

- `api_sha256`: `1aef9256b064c15c2d37af9e34eb5bd0d9da269fa947e24607dc0e86710c7527`
- `file_sha256`: `cd3ff431472608ad96aa9d18537bb7d1087b7f60c265f34390ab43b9afa4ff5f`

**Nomi riesposti da questo package**

- `configurazioni (da )`
- `localizza_stringhe (da localize)`
- `cache_salva (da configurazioni.imgcache)`
- `cache_svuota (da configurazioni.imgcache)`
- `CACHE (da configurazioni.imgcache)`
- `descrizioni (da configurazioni)`
- `content (da shortcuts)`
- `i18n (da shortcuts)`
- `assets (da )`
- `pagebundle (da )`
- `settings (da settings)`

## `sitekit.assets`

File: `src/sitekit/assets/__init__.py`

- `api_sha256`: `d3ad19ff54239ab2de956d22cc7f189ba4a9ff55af75c8a5d495dd9081984d88`
- `file_sha256`: `c4d61aca7690d5d6ed6166bd8ed92e75d386cbb7bec52e700fae923dbc9241f2`

Pipeline degli asset: dai sorgenti alla cartella servita.

    resources/           sorgenti DA ELABORARE (immagini da ridimensionare)
    static/              sorgenti GIÀ PRONTI (css, js, font)
    content/<bundle>/    immagini dei page bundle, accanto al markdown
            │
            │  conversione (images.copy)
            ▼
    .cache/assets/       output delle conversioni
            │
            │  assets.build()
            ▼
    assets/              unica cartella servita in dev e copiata nel build

`resources/` e `static/` sono le uniche cartelle che si modificano a
mano; `assets/` e `.cache/` sono generate e vanno in .gitignore.

`__all__`: `build`, `cartella_generati`, `destinazione`, `register`, `url`

**Nomi riesposti da questo package**

- `build (da costruzione)`
- `register (da costruzione)`
- `cartella_generati (da percorsi)`
- `destinazione (da percorsi)`
- `url (da percorsi)`

## `sitekit.assets.costruzione`

File: `src/sitekit/assets/costruzione.py`

- `api_sha256`: `c92240c66cc40a60aef6dd95456cd6cf1d657421fdd841a1668258c1d7bd1681`
- `file_sha256`: `4cc4c77e6ae477943b38714746c82745fcee975d2142aee173705b791f86dd6c`

**Funzioni**

```python
def build(pulisci: bool = False) -> int
```

Unisce le sorgenti degli asset dentro ASSETS_DIR.

Confluiscono, in quest'ordine, gli asset generati in
CACHE_DIR/assets, i sorgenti da elaborare di RESOURCES_DIR e i
sorgenti già pronti di STATIC_DIR. La struttura delle cartelle
viene ricopiata tale e quale: `static/css/style.css` diventa
`assets/css/style.css`.

La copia è incrementale — un file viene riscritto solo se manca
o se differisce per dimensione o data — quindi la funzione può
essere richiamata a ogni avvio dell'applicazione a costo quasi
nullo.

Args:
    pulisci: se True rimuove da ASSETS_DIR i file che non
        provengono più da nessuna sorgente, e le cartelle
        rimaste vuote.

Returns:
    Numero di file effettivamente copiati.

```python
def register(app: object, costruisci: bool = True) -> None
```

Rende ASSETS_DIR raggiungibile dal server di prova.

Se l'applicazione è già stata costruita puntando lo static
folder ad ASSETS_DIR non serve nessuna route in più; altrimenti
ne viene aggiunta una dedicata, così gli asset si vedono anche
in sviluppo.

Per il freeze conviene comunque costruire l'app così:

    app = Flask(__name__,
                static_folder=settings.ASSETS_DIR,
                static_url_path=settings.ASSETS_URL)

perché Frozen-Flask copia da sé lo static folder, mentre una
route con segnaposto `<path:>` non è scopribile da sola.

Args:
    app: istanza dell'applicazione Flask.
    costruisci: se True chiama `build()` subito dopo.

## `sitekit.assets.percorsi`

File: `src/sitekit/assets/percorsi.py`

- `api_sha256`: `37ca1b03ac5ce093228c7aa52e7922fb3982530be180cc836f6e7721a5363000`
- `file_sha256`: `ecaa704dae38a965c2da1021e960ae5136670d95b187536f8a996506e8a618a4`

**Funzioni**

```python
def cartella_generati() -> Path
```

Radice degli asset generati, dentro la cache.

È un mirror parziale di ASSETS_DIR: ci finisce solo ciò che la
libreria produce (immagini convertite, file copiati dai page
bundle), così una `assets.build(pulisci=True)` può azzerare la
cartella finale senza costringere a riconvertire tutto.

Returns:
    Path di CACHE_DIR / "assets".

```python
def destinazione(sottopercorso: str | Path = '') -> Path
```

Percorso su disco in cui scrivere un asset generato.

È quello che si passa come `destination_folder` a
`images.copy`. La cartella viene creata se non esiste.

Args:
    sottopercorso: percorso relativo alla radice degli asset,
        ad esempio "images/chi-siamo".

Returns:
    Path assoluta dentro CACHE_DIR / "assets".

```python
def url(sottopercorso: str | Path = '') -> str
```

URL pubblico corrispondente a un sottopercorso degli asset.

`destinazione()` e `url()` sono le due facce dello stesso
percorso: usarle in coppia è ciò che impedisce a dove si scrive
e a cosa si stampa di divergere.

Args:
    sottopercorso: percorso relativo alla radice degli asset,
        ad esempio "images/chi-siamo".

Returns:
    URL assoluto, ad esempio "/assets/images/chi-siamo".

## `sitekit.cache`

File: `src/sitekit/cache/__init__.py`

- `api_sha256`: `890d690ab049c52fef0de3c2ea895102ca87d1f1a7c0a8b843834f7498255a1b`
- `file_sha256`: `2748c075de5a0f4f55c616401c558d2a2206112ad64b8a6f8277f9c10f8be5ef`

**Nomi riesposti da questo package**

- `Path (da pathlib)`
- `shortcodes (da sitekit)`
- `settings (da sitekit.settings)`
- `ram (da )`

**Funzioni**

```python
def load(input_file: Path) -> dict | None
```

```python
def clean()
```

Ripulisce la cartella di cache,
cancellando tutti i file non utilizzati
durante l'esecuzione.

```python
def prune(days: int = 60) -> None
```

Cancella tutti i file in CACHE_DIR più vecchi di N giorni.

Va chiamata esplicitamente una volta a ogni avvio
dell'applicazione per tenere la cartella di cache sotto
controllo: l'importazione del modulo non la invoca.

Args:
    days: Numero di giorni oltre i quali un file viene
        considerato scaduto e cancellato. Default: 60.

## `sitekit.cache.ram`

File: `src/sitekit/cache/ram.py`

- `api_sha256`: `8dc87f5117648857f3b7bbdf0161b1880c4bc120490196bec22e5328f21b6713`
- `file_sha256`: `c82c90b05fa8639b0533fa8dc019e6d75fcbd7549e1168b49c9bbf465a2b9bfc`

**Costanti**

- `CACHE` = `{}`

**Funzioni**

```python
def carica(chiave: str) -> dict | None
```

```python
def salva(chiave: str, valore: object) -> bool
```

## `sitekit.configurazioni`

File: `src/sitekit/configurazioni/__init__.py`

- `api_sha256`: `c7fe2c8f4dc284fa7e38775ece694cc4792f895169ba7b6641dbdc2f31db4001`
- `file_sha256`: `bdcc259194b43785be5674f5de53642d5f0d7ca0f2f45ea6ea504f8bd3b57a76`

**Nomi riesposti da questo package**

- `Path (da pathlib)`
- `datetime (da datetime)`
- `timedelta (da datetime)`
- `format_currency (da babel.numbers)`
- `format_date (da babel.dates)`
- `image_copier (da images)`
- `marca_come_convertite (da images)`
- `cache (da sitekit)`
- `jsonld (da sitekit)`
- `descrizioni (da sitekit.configurazioni)`
- `images (da sitekit)`
- `assets (da sitekit.assets)`
- `settings (da sitekit.settings)`

**Costanti**

- `CACHE` = `{}`

**Funzioni**

```python
def elenca()
```

Elenca i ristoranti per i quali sono
disponibili configurazioni.

```python
def vuoto(slug: str = '', lingua: str = 'en') -> dict
```

Restituisce un dict di configurazione
'quasi vuoto', che però contiene il tema
di default del sito

Args:
    slug: Slug del ristorante
    lingua: Lingua da utilizzare

Returns:
    dict: Un dizionario con i
            parametri di configurazione minimi
            per non far crashare il server

```python
def carica(sito: str, lingua: str) -> dict
```

Carica i parametri di configurazione del ristorante specificato.

args:
    sito (str): Il codice del ristorante (es: "scla").
    lingua (str): La lingua in cui caricare i parametri (es: "it", "en").

returns:
    dict: Un dizionario con i parametri del ristorante.

## `sitekit.configurazioni.descrizioni`

File: `src/sitekit/configurazioni/descrizioni/__init__.py`

- `api_sha256`: `8c58c8968a20f3fb3696288fc4be8545b724a078045fc1cc8051e0472306cd7e`
- `file_sha256`: `96127530152bbd5fa0b609f5c4da3487065bb440883945e01a1c7cb43101c7e4`

**Nomi riesposti da questo package**

- `settings (da sitekit.settings)`
- `cache (da sitekit)`

**Funzioni**

```python
def elenca(sito: str) -> list[str]
```

Restituisce un elenco delle lingue per cui esiste
una descrizione del ristorante.

```python
def esiste(sito: str, lingua: str) -> bool
```

Controlla se esiste una descrizione per il ristorante
nella lingua specificata.

```python
def carica(sito, lingua) -> tuple[str | None, str]
```

Carica la descrizione del ristorante,
se presente in una sottocartella chiamata
'descriptions'

```python
def carica_fallback(sito, lingua)
```

Carica le descrizioni del ristorante, se
presente in un file descriptions.yaml. E
poi restituisce quella nella lingua in
cui stiamo attualmente lavorando.

```python
def salva(sito, lingua, testo)
```

Salva la descrizione del ristorante in un file

## `sitekit.configurazioni.images`

File: `src/sitekit/configurazioni/images.py`

- `api_sha256`: `0297c7887d76b9fe874d6375e7e71230858a41970705e7fa4cc276529d3351cb`
- `file_sha256`: `9e7780f9a3ffad7e03a534c195a7311bbf22ca66a0b6b2dd85f4d38f803fe43a`

**Funzioni**

```python
def image_copier(folder_name: Path, image_path: Path)
```

Preleva un'immagine selezionata dalla cartella `places/<folder_name>`
la converte nei formati .avif, .webp e .jpg riducendone le dimensioni,
ed infine la salva nella cartella `static/images/<folder_name>`.

args:
    folder_name (Path): Contiene il nome della cartella da cui viene
                        prelevata l'immagine (es: "scla")
    image_path (Path): È il percorso assoluto al file immagine nella
                        cartella "content"

returns:
    str: Il nome del file indicato da <folder_name> senza estensione.

```python
def marca_come_convertite(folder_name)
```

Marca la cartella come convertita, così non la converte più
durante la sessione di lavoro attuale.

## `sitekit.configurazioni.imgcache`

File: `src/sitekit/configurazioni/imgcache.py`

- `api_sha256`: `c78e2fd7167a97fcd86118e4b7ec2d4bfda497a018d7b6b406b30ad66f30a64f`
- `file_sha256`: `7b6b8003f9406ef0c3177cef0deae36d01f3e3bd63551159401d9629c756bc5d`

**Costanti**

- `CACHE` = `cache_carica()`

**Funzioni**

```python
def cache_carica() -> dict
```

```python
def cache_svuota() -> None
```

```python
def cache_aggiungi(percorso: Path) -> bool
```

Ritorna True se il file è invariato (nessuna conversione da fare),
oppure False se è nuovo o modificato (serve rigenerare).

```python
def cache_salva() -> None
```

## `sitekit.images`

File: `src/sitekit/images/__init__.py`

- `api_sha256`: `ff059c280cabeb4f2888629a353c7e8051af90bae5d910970e3244fbc13bfc05`
- `file_sha256`: `5cdc4a1519353747b64f4504cd2adca60218514a0d3a45d988cd529b902934ba`

**Nomi riesposti da questo package**

- `settings (da sitekit.settings)`
- `Path (da pathlib)`
- `images (da )`
- `imgcache (da )`
- `PictureClass (da picture_class)`

**Funzioni**

```python
def copy(source_image: Path, destination_folder: Path, aspect_ratio: str = 'unchanged', anchor: str = 'middle', alt: str = '', base_url: str | None = None) -> PictureClass
```

Copies an image file to a specified destination, creating multiple resized
versions of the image with predefined sizes. Ensures the source file exists
and the destination folder is created, if not already existent.

Parameters:
    source_image (Path): The path of the image file to be copied.
    destination_folder (Path): The path of the folder where the image
        and its resized copies will be saved.
    aspect_ratio (str): The aspect ratio to maintain for the resized images.
        Default is "unchanged". Examples: "2:3", "4:3", "16:9", "9:16"
    anchor (str): The vertical anchor position for cropping the image.
    alt (str): Testo alternativo per il tag <img>. Importante per
        accessibilità e SEO. Default stringa vuota.
    base_url (str | None): URL pubblico della cartella di destinazione,
        di norma ottenuto da `assets.url(...)`. Se non viene passato,
        PictureClass deduce l'URL dal percorso su disco.

Returns:
    PictureClass: An instance of PictureClass representing the folder
        containing the copied images.

Raises:
    FileNotFoundError: If the source image file does not exist or is not
        a valid file.

## `sitekit.images.images`

File: `src/sitekit/images/images.py`

- `api_sha256`: `339a9ab3dd98e357f10fae8bf89c405d88096e2b33e726b279413343439f8640`
- `file_sha256`: `df67bdedf40248ee4751502d64e72ea14544474245dde1cc4b2169feb6e8b209`

**Funzioni**

```python
def copy_single(input_file: Path, output_folder_path: Path, longest_side: int = 1200, output_formats: list = None, aspect_ratio = 'unchanged', anchor: str = 'middle') -> bool
```

Copies and processes an image from the input path to the output folder, resizing and converting it to specified formats.

This function takes an input image and applies a series of transformations while ensuring efficient reuse of previously processed or cached image data.
The transformations include optional cropping to a specified aspect ratio, resizing the longest side, and exporting the image in multiple output formats.
The function supports formats including AVIF, WebP, and JPEG. Output images are stored in the specified output directory.

Arguments:
    input_file (Path):
        The path to the input image file.
    output_folder_path (Path):
        The directory where processed images
        will be stored.
    longest_side (int, optional):
        Maximum allowed size for the longest
        side of the image. Default is 1200 pixels.
    output_formats (list, optional):
        List of desired output formats. Supported
        values are "avif", "webp", and "jpeg".
        Defaults to ["avif", "webp", "jpeg"].
    aspect_ratio (str, optional):
        Specifies whether to crop the image to a
        given aspect ratio. Defaults to "unchanged".
    anchor (str, optional):
        Vertical crop anchor when the image is taller than the target ratio.
        One of "top", "middle", or "bottom". Defaults to "middle".

Returns:
    bool:
        True if the operation is successful and
        at least one image is saved, False otherwise.

Raises:
    ValueError:
        If an unsupported format is specified in the output_formats list,
        or if `anchor` is not one of "top", "middle", "bottom".

## `sitekit.images.imgcache`

File: `src/sitekit/images/imgcache.py`

- `api_sha256`: `3b1eb946b805471b2aa7518cf71f8407b5107bcfde11de6bdb3e17617d0ac943`
- `file_sha256`: `a1c2509c1e6196c8b4281f28aa85515bae23bf14256989af9ca090b9408627c8`

**Costanti**

- `CACHE` = `set()`

**Funzioni**

```python
def svuota() -> None
```

Svuota il file indice

```python
def verifica_e_aggiungi(input_file: Path, longest_side: int, output_path_folder: Path, aspect_ratio: str = 'unchanged', anchor: str = 'middle') -> tuple[bool, str | None]
```

Cerca uno specifico file all'interno della tabella degli hash
che ha memorizzato nel file json in cache.

Ritorna una tupla (da_elaborare, sha1):
- da_elaborare=True  → il file è nuovo o i file su disco mancano: bisogna rigenerare
- da_elaborare=False → il file era già in cache e i file su disco esistono: skip
- sha1               → hash SHA-1 del file sorgente (None se il file non esiste),
                       restituito per evitare di ricalcolarlo nel chiamante

```python
def clean() -> None
```

Rimuove da CACHE le entry non toccate durante la build
corrente e persiste il risultato su disco.

Va chiamata a fine build, dopo aver processato tutte le
immagini, esattamente come cache.clean() per i pickle.
Le entry orfane — immagini rimosse o non più referenziate
nei contenuti — vengono eliminate da imagesdb.json.

```python
def salva() -> None
```

## `sitekit.images.picture_class`

File: `src/sitekit/images/picture_class.py`

- `api_sha256`: `4b843e3658dd066c8639b6469abf7a517f90cca9a6f8714026e05d202786e3d3`
- `file_sha256`: `5805d29f409e8e41777a2f66776f081b0b9694a3537ef841db3b71b7e17ba4ef`

### `class PictureClass`

**Metodi**

```python
def __init__(self, folder: Path, alt: str = '', base_url: str | None = None)
```

Args:
    folder: cartella su disco che contiene i breakpoint
        generati, il cui nome è lo stem dell'immagine
        sorgente.
    alt: testo alternativo per il tag <img>.
    base_url: URL pubblico della cartella. Va passato da chi
        conosce la pipeline degli asset (di norma
        `assets.url(...)`); se manca, l'URL viene dedotto dal
        percorso su disco, che funziona solo finché i file
        stanno sotto una cartella chiamata "static".

## `sitekit.jsonld`

File: `src/sitekit/jsonld/__init__.py`

- `api_sha256`: `784d114313fb81362ac8bf282a8246ad430f0fb5df8ca282af152bd28a67d6f3`
- `file_sha256`: `bb5a79bdb003cb843aa59090b57e0c9c0ee1dc4620c84b551eeabbc2f15b3437`

**Nomi riesposti da questo package**

- `urljoin (da urllib.parse)`
- `schema (da )`
- `menu (da )`

**Funzioni**

```python
def clear(type_: str = 'Restaurant') -> dict
```

```python
def import_(data: dict)
```

```python
def add_product(data: dict)
```

```python
def debug() -> dict
```

```python
def generate() -> str
```

## `sitekit.jsonld.menu`

File: `src/sitekit/jsonld/menu.py`

- `api_sha256`: `350b90329c6f6197076427231c38a7a9490144e74e0b9a1dc782dab245e6365a`
- `file_sha256`: `49dc5e601b317d1b1d478b3d1bf8a50f8345b092f3a48d1796266f3adecd6c8e`

**Funzioni**

```python
def new()
```

```python
def add_dish(name: str, description: str = None, image: Path = None, price: float = None)
```

## `sitekit.jsonld.schema`

File: `src/sitekit/jsonld/schema.py`

- `api_sha256`: `31da952caea594d96c173b372342b93e8764f8aece30b85e59e5f7d89ec55b52`
- `file_sha256`: `7be792788c843cf5e2f00a1669d5e9de1128b3a2740dec029ba442cd63285b7b`

**Funzioni**

```python
def new(type_: str = 'Restaurant')
```

## `sitekit.localize`

File: `src/sitekit/localize/__init__.py`

- `api_sha256`: `a32940845b92d7eb38d812f6e86fcb3f216002955f4e3929adde87fd2ec9f81e`
- `file_sha256`: `56f9d6bef586bc8070ae58a3a185184e2dc8e026b21cd875a35c05d6c97fbf89`

**Nomi riesposti da questo package**

- `get_day_names (da babel.dates)`
- `settings (da sitekit.settings)`

**Funzioni**

```python
def localizza_stringhe(lingua)
```

## `sitekit.memos`

File: `src/sitekit/memos/__init__.py`

- `api_sha256`: `ae17689cb565bc44f907ea9e9e1c269cd5b49c00badec06f3f1d942c6bb56ae4`
- `file_sha256`: `c36135e2015b2dbb15ef0b6169743c56aade30a6d4b00a772d7441a7d2d632e0`

**Nomi riesposti da questo package**

- `Path (da pathlib)`

**Costanti**

- `CONFIG` = `Config(base_url='', token='')`

**Funzioni**

```python
def set_token(token: str | Path) -> None
```

```python
def set_base_url(base_url: str) -> None
```

```python
def always_force_a_title(force_a_title: bool) -> None
```

```python
def wrap_titles_at(wrap_titles_at: int) -> None
```

```python
def get(limit: int = 6) -> list[dict]
```

Elenca tutte le note di un server Memos

```python
def test(dati: list[dict]) -> None
```

### `class Config`

**Metodi**

```python
def __init__(self, base_url: str, token: str | Path)
```

```python
def token(self)
```
*(property)*

```python
def token(self, valore: str | Path)
```

## `sitekit.openings`

File: `src/sitekit/openings/__init__.py`

- `api_sha256`: `7a20a6de024cdf5284977f9f04ee09f83da49ab6d7be4fb518ce9295b8675e02`
- `file_sha256`: `b944a053cd564cef06f3d9aef7ec8c46637a58f2f781954e8eae9d0771d5afcb`

**Nomi riesposti da questo package**

- `Path (da pathlib)`
- `OpeningsClass (da classes)`
- `settings (da sitekit.settings)`

**Funzioni**

```python
def load(config_file: Path) -> OpeningsClass
```

## `sitekit.openings.classes`

File: `src/sitekit/openings/classes/__init__.py`

- `api_sha256`: `2c578d3e3e6a5b114c1e71f7ad617330ea0ce03d2131c21b4e9e9c3bb3400a59`
- `file_sha256`: `fbd99057d62e8886a399967712620358e13a3033b5ea776db8bdf60bc8e70069`

**Nomi riesposti da questo package**

- `OpeningsClass (da openingsclass)`

## `sitekit.openings.classes.dayopeningclass`

File: `src/sitekit/openings/classes/dayopeningclass.py`

- `api_sha256`: `c5a5dca11da2544daae5aa0920a312aa45a8b8718a059b0706b9f2446f930bc4`
- `file_sha256`: `090067fd8bcca0fdf4d73ad6b0d353205fc153bea180e9d6f44b133b7754a762`

### `class DayOpeningClass`

**Metodi**

```python
def __init__(self, config_text: list)
```

```python
def closed(self)
```

```python
def count(self)
```

```python
def turn(self, index: int)
```

```python
def to_string(self, separator: str = ' | ')
```

## `sitekit.openings.classes.holidayclass`

File: `src/sitekit/openings/classes/holidayclass.py`

- `api_sha256`: `0687d659b92039225421c9127895e91cbf622ec7f5b16ba44d8d5c91baab6ed3`
- `file_sha256`: `b732b48e7f386c3b7547225f0d024010480122e05a069c38e91e09c86ba7568a`

### `class HolidayClass`

**Metodi**

```python
def __init__(self, label: str, data: list)
```

```python
def easter_gauss(year)
```

## `sitekit.openings.classes.holidaylistclass`

File: `src/sitekit/openings/classes/holidaylistclass.py`

- `api_sha256`: `1a68890633ca457fa8af9a19b46032ee7d1e3e6f374baf9fdf247706c6510e4a`
- `file_sha256`: `70fc78fe9cf08598eff3b55d05bd1ee03aec60abbf57283b88eaebb218af08a1`

### `class HolidayListClass`

**Metodi**

```python
def __init__(self)
```

```python
def append(self, label: str, data: list)
```

## `sitekit.openings.classes.openingsclass`

File: `src/sitekit/openings/classes/openingsclass.py`

- `api_sha256`: `060ba3bb731602bc28ac7bb9318cc69b6fcf1ff4efd9c16c057350b61c05c83f`
- `file_sha256`: `9a80b0c3f86a3c5dee9ef2a1b5b6cfa2b09c8fe38b5a5b76647730b921d7687e`

### `class OpeningsClass`

**Metodi**

```python
def __init__(self, config_text: dict)
```

```python
def weekday(self, day: int) -> DayOpeningClass
```

```python
def monday(self) -> DayOpeningClass
```

```python
def tuesday(self) -> DayOpeningClass
```

```python
def wednesday(self) -> DayOpeningClass
```

```python
def thursday(self) -> DayOpeningClass
```

```python
def friday(self) -> DayOpeningClass | None
```

```python
def saturday(self) -> DayOpeningClass | None
```

```python
def sunday(self) -> DayOpeningClass | None
```

```python
def today(self)
```

```python
def tomorrow(self)
```

```python
def get(self, _date: date) -> DayOpeningClass
```

## `sitekit.openings.classes.turnclass`

File: `src/sitekit/openings/classes/turnclass.py`

- `api_sha256`: `d50276826b9e56f3de60dfdba6def0806086a4b54d6d7d8de213cdbd3e14360c`
- `file_sha256`: `fab77eb109a9df6be3bdda16e1d6fc5bc1f7257ee1459d44e3ffc71d52d87d08`

### `class TurnClass`

**Metodi**

```python
def __init__(self, config_text: str)
```

```python
def closed(self) -> bool
```

```python
def to_string(self, separator: str = ' - ')
```

## `sitekit.pagebundle`

File: `src/sitekit/pagebundle/__init__.py`

- `api_sha256`: `99ac4ba347e5dc2ae4953763235fca6bfb16d58b2926d700aba735052c8ca901`
- `file_sha256`: `6ae67749faebfe23a134c3a6f4fc348b6f81ede3a196f02a890e02d9473ecabf`

**Nomi riesposti da questo package**

- `datetime (da datetime)`
- `Path (da pathlib)`
- `settings (da sitekit.settings)`
- `media (da )`

**Funzioni**

```python
def load(percorso: str | Path, copia_asset: bool = True) -> dict
```

Carica un page bundle, cioè una pagina e i suoi asset.

Una pagina può stare tutta in un file solo oppure essere spezzata
su più file secondo la convenzione
`<stem>[.<sezione>]*[.<lingua>].md`: i segmenti di 3 o più
caratteri sono chiavi di sezione annidabili, quello finale di
esattamente 2 caratteri è un codice lingua. Le due forme
producono lo stesso identico dizionario.

Esempi (con stem "index"):

    index.md                    → radice
    index.intro.md              → dati["intro"]
    index.history.gallery.md    → dati["history"]["gallery"]
    index.intro.en.md           → dati["localization"]["en"]["intro"]

Le sottocartelle con nome di 2 caratteri sono cartelle-lingua ed
equivalgono al suffisso lingua sul nome file: `en/index.intro.md`
vale quanto `index.intro.en.md`.

Gli asset della cartella vengono convertiti e copiati sotto
`assets/`, e i riferimenti relativi nel markdown vengono
riscritti di conseguenza.

Args:
    percorso: cartella del page bundle, oppure percorso esplicito
        del file indice.
    copia_asset: se False non tocca il disco e non riscrive i
        riferimenti. Utile quando servono solo i dati.

Returns:
    Dict con il frontmatter di tutti i file fusi insieme, più
    "slug" (nome del bundle), "content"/"content_raw" a ogni
    livello che ha del testo, "localization" con le lingue
    diverse da settings.DEFAULT_LANGUAGE, e — se presenti —
    "date" e "cover".

Raises:
    FileNotFoundError: se il percorso non esiste o la cartella non
        contiene né index.md né _index.md.
    ValueError: se un nome di file non segue la convenzione.

```python
def load_collection(path: Path) -> list[dict]
```

Carica tutti i page bundle di una cartella, ordinati per data.

Serve per blog e news, dove ogni sottocartella è un post. Le
pagine senza `date` nel frontmatter la ricavano dalla data di
creazione della cartella, così l'ordinamento è sempre possibile.

Args:
    path: cartella che contiene i page bundle.

Returns:
    Lista di dizionari come quelli di `load`, dal più vecchio al
    più recente.

```python
def localizzato(dati: dict, lingua: str) -> dict
```

Restituisce la pagina nella lingua richiesta, con fallback.

La radice (lingua di default) viene fusa con
`dati["localization"][lingua]`: le chiavi tradotte vincono, le
altre restano nella lingua di default invece di sparire.

Args:
    dati: dizionario prodotto da `load`.
    lingua: codice della lingua desiderata.

Returns:
    Un nuovo dizionario senza la chiave "localization".

## `sitekit.pagebundle.media`

File: `src/sitekit/pagebundle/media.py`

- `api_sha256`: `cd33d814895402cf573ceda3f6a1abc7bde6925a260725204939a881b8721d31`
- `file_sha256`: `aee22b98516086064c22e77e56f847440fa48bc636fe7ccfe073af426d989f9b`

**Costanti**

- `TIPI_IMMAGINE` = `('.jpg', '.jpeg', '.png')`
- `TIPI_IGNORATI` = `('.md', '.markdown', '.yaml', '.yml', '.json')`

**Funzioni**

```python
def destinazione(slug: str) -> Path
```

Cartella su disco in cui finiscono gli asset del bundle.

Args:
    slug: nome del page bundle.

Returns:
    Path dentro CACHE_DIR/assets, creata se non esiste.

```python
def url(slug: str) -> str
```

URL pubblico degli asset del bundle.

Args:
    slug: nome del page bundle.

Returns:
    Ad esempio "/assets/images/primo-post".

```python
def copia(cartella: Path, slug: str) -> str | None
```

Converte e copia gli asset di un page bundle.

Le immagini passano per `images.copy`, che genera i quattro
breakpoint in AVIF, WebP e JPEG dentro una sottocartella con lo
stem del file. I file di contenuto vengono ignorati, tutto il
resto viene copiato tal quale.

Args:
    cartella: root del page bundle.
    slug: nome del page bundle, che dà il nome alla cartella di
        destinazione.

Returns:
    Lo stem del primo file immagine che contiene "_cover" nel
    nome, oppure None se non ce n'è nessuno.

## `sitekit.pagebundle.nomi`

File: `src/sitekit/pagebundle/nomi.py`

- `api_sha256`: `c14ced8cd6d72b634f9e700b78997b2a1b156da58e385f43dffe377251b85ee9`
- `file_sha256`: `252f281fd8de6299d4aeb8795b954d566b24ffe06edc75831c019ac29117b6f3`

**Costanti**

- `LUNGHEZZA_LINGUA` = `2`
- `LUNGHEZZA_SEZIONE_MINIMA` = `3`

## `sitekit.privacy`

File: `src/sitekit/privacy/__init__.py`

- `api_sha256`: `3e5f924d5f5befb1e940061a4c583f9a8a43bb5a435cd7c5981437c89884fc01`
- `file_sha256`: `af823c1378e492d48acced3b03357c73d0caeed6a523f48765b49d73909339ba`

**Nomi riesposti da questo package**

- `settings (da sitekit.settings)`

**Funzioni**

```python
def esiste(lingua: str) -> bool
```

Indica se la privacy policy nella lingua
indicata esiste sul disco

```python
def carica(lingua: str, params: dict = {}) -> dict | None
```

```python
def salva(lingua: str, testo: str) -> None
```

Salva la privacy policy per la lingua
indicata sul disco

## `sitekit.robots`

File: `src/sitekit/robots/__init__.py`

- `api_sha256`: `cf7d1fd7a07641b33d1ec8e87eb70574ddbaf48faae3599e4b45090a916170ae`
- `file_sha256`: `50eb4436aa177c05b43d3a69aee7013d1529832202c42c162852edb677034576`

**Nomi riesposti da questo package**

- `settings (da sitekit.settings)`

**Funzioni**

```python
def generate()
```

## `sitekit.router`

File: `src/sitekit/router/__init__.py`

- `api_sha256`: `6800513c8678a3430bf1eb4786b47e6e012a463f27f4dc951572fe49ef9dc2f6`
- `file_sha256`: `233c645b8dfdd3dfd3135c201680551150a30c8e8561650ec3a0609e2d2d6a8c`

**Nomi riesposti da questo package**

- `Router (da router)`

## `sitekit.router.router`

File: `src/sitekit/router/router.py`

- `api_sha256`: `87c4c604f79efe709e67f2fdd2b2b902b9b2eff230f829d9b4a40086b41c105d`
- `file_sha256`: `3ae9dc97904713e30e13281289d7f16c5860d25550d4306d63d7b8e34782ba57`

### `class Router`

Risolve URL multilingua in percorsi di file di contenuto
e viceversa, seguendo la convenzione page-bundle.

La lingua di default viene servita senza prefisso nell'URL
e corrisponde a file index.md. Le lingue non-default hanno
un prefisso di esattamente 2 caratteri nell'URL e corrispondono
a file index.<lingua>.md.

Esempi:

    /chi-siamo        → CONTENT_DIR/chi-siamo/index.md
    /en/chi-siamo     → CONTENT_DIR/chi-siamo/index.en.md
    /                 → CONTENT_DIR/index.md
    /en/              → CONTENT_DIR/index.en.md

**Metodi**

```python
def __init__(self, cartella_base: Path | None = None) -> None
```

Args:
    cartella_base (Path | None): Directory radice dei contenuti.
        Se non specificata, viene usato settings.CONTENT_DIR.

```python
def aggiungi_alias(self, cartella_alias: str, cartella_destinazione: str)
```

Aggiunge un alias all'elenco delle cartelle gestite.

Esempio:
aggiungi_alias("about-us", "chi-siamo")

se successivamente richiamo Router.da_url("/en/about-us")
mi deve restituire "{self.base}/chi-siamo/index.en.md"

Args:
    cartella_alias (str): Nome della cartella (senza percorso)
                             che deve fungere da alias
    cartella_destinazione (str): Nome della cartella (senza percorso)
                                 a cui va ridirezionato l'output

```python
def da_url(self, url: str) -> tuple[Path, str]
```

Converte un URL relativo nel percorso del file di contenuto
corrispondente e nel nome del template da usare per renderizzarlo.

Il primo segmento di 2 caratteri viene trattato come codice
lingua (es. "en"); tutti gli altri URL vengono trattati come
lingua di default.

L'ordine di ricerca del file è:
1. index.md / index.<lingua>.md
2. _index.md / _index.<lingua>.md
3. alias registrati via aggiungi_alias()

Non è possibile risalire fuori dalla cartella base tramite
sequenze come `..`.

Args:
    url (str): URL relativo, es. "/chi-siamo" o "/en/about-us".

Returns:
    tuple[Path, str]: Percorso assoluto del file di contenuto
        e nome del template letto dal campo "template" nel
        frontmatter. La stringa è vuota se il campo non esiste.

Raises:
    ValueError: Se l'URL tenta di uscire dalla cartella base.
    FileNotFoundError: Se il file non esiste e non c'è nessun
        alias corrispondente.

```python
def verso_url(self, percorso: Path) -> str
```

Converte il percorso di un file di contenuto nell'URL
corrispondente.

Supporta le varianti index e _index, con e senza suffisso lingua:

- index.md / _index.md → lingua di default, URL senza prefisso
- index.<lingua>.md / _index.<lingua>.md → URL con /<lingua>/

Esempi:

    CONTENT_DIR/chi-siamo/index.md     → /chi-siamo/
    CONTENT_DIR/chi-siamo/_index.md    → /chi-siamo/
    CONTENT_DIR/chi-siamo/index.en.md  → /en/chi-siamo/
    CONTENT_DIR/chi-siamo/_index.en.md → /en/chi-siamo/
    CONTENT_DIR/index.md               → /
    CONTENT_DIR/index.en.md            → /en/

Il suffisso è un codice lingua solo se lungo esattamente 2
caratteri: i file di sezione di sitekit.pagebundle, come
index.intro.md, non sono pagine e sollevano ValueError.

Args:
    percorso (Path): Percorso del file di contenuto.

Returns:
    str: URL relativo con slash iniziale (e finale tranne
        per la homepage della lingua di default).

Raises:
    ValueError: Se il file non segue le convenzioni attese
        o non è dentro la cartella base.

```python
def register(self, app: object) -> None
```

Registra il Router nei global di Jinja2 dell'app Flask.

Dopo la chiamata, nei template è disponibile `router`
come variabile globale:

    {{ router.verso_url(percorso) }}
    {{ router.da_url('/chi-siamo') }}

Args:
    app (object): Istanza dell'applicazione Flask.

## `sitekit.rssreader`

File: `src/sitekit/rssreader/__init__.py`

- `api_sha256`: `20a734ed3ebb18c9d96e3850224f210c361201f2529a620ecc196d9806ece118`
- `file_sha256`: `d45dc361af653458a63ba3806f887c769f0dea254bf75237c51742dad699647f`

**Nomi riesposti da questo package**

- `strip_html (da _utils)`

**Funzioni**

```python
def load(url: str, source: str = 'generic', limit: int = 6, body_limit: int = 500) -> list[dict]
```

Scarica e interpreta un feed RSS restituendo una lista di articoli.

Args:
    url:        URL del feed RSS.
    source:     Tipo di sorgente ("memos", "wordpress").
                Determina come vengono estratti image e body.
    limit:      Numero massimo di articoli da restituire (default 6).
    body_limit: Lunghezza massima del body in caratteri (default 500).
                Se il testo è più lungo viene troncato e termina con "…".
                Passare 0 o None per non troncare.

Returns:
    Lista di dizionari con chiavi: title, image, body, url.
    Tutti i campi testuali sono testo puro, privi di tag HTML.

## `sitekit.rssreader.memos`

File: `src/sitekit/rssreader/memos.py`

- `api_sha256`: `92e3f95d9be5198b8d0c6b0473042c9818885e2dd8ad98e7ca08cd537b20e262`
- `file_sha256`: `d1ee4150e4915f99550467e233425898eef0314827e9f54b796d173916decf9e`

**Funzioni**

```python
def importa(entry) -> dict
```

Estrae body e image da una entry feedparser di un feed Memos.

Memos spesso non compila il campo title (o lo lascia vuoto):
in quel caso si usano le prime parole del body come titolo.
Le immagini sono tipicamente in <enclosure> (jpeg/png/gif);
eventuali enclosure video/* o audio/* vengono ignorati.

## `sitekit.rssreader.wordpress`

File: `src/sitekit/rssreader/wordpress.py`

- `api_sha256`: `502127c44ce28ed46e272a2aa670e908d74396001955ae461784a186ab15c42d`
- `file_sha256`: `38c0367a69247d49c9a79dab51982d928043d0a96a9099ff10e17a65a8877833`

**Funzioni**

```python
def importa(entry) -> dict
```

Estrae body e image da una entry feedparser di un feed WordPress.

WordPress pubblica il testo completo in content:encoded (entry.content),
con fallback sull'excerpt in entry.summary.
L'immagine in evidenza si trova tipicamente in media:content,
media:thumbnail, negli enclosures, oppure come prima <img> nel body.

## `sitekit.settings`

File: `src/sitekit/settings.py`

- `api_sha256`: `9b4ff52367ed1de06c0fb81aaae97e0f62b36bd4c79c49c28539fcfef5f3f511`
- `file_sha256`: `f5b07ff3c615801794d8f6724976162be1f12c1eccabfec151ec17e89bbd6d1f`

### `class SettingsClass`

**Metodi**

```python
def set_i18n_dir(self, path: Path)
```

```python
def __init__(self)
```

## `sitekit.shortcodes`

File: `src/sitekit/shortcodes/__init__.py`

- `api_sha256`: `06cd0408d47dd823306a2bd5e3bc08bdece5f32dd53ae0c1a109c755fe8de374`
- `file_sha256`: `9a19f0e32b96567265b7b660d3ea0b5296d70890b7561750dd2bffc0cf7c2d8c`

**Nomi riesposti da questo package**

- `ProcessoreShortcode (da processore)`
- `percorsi_template (da scoperta)`

**Funzioni**

```python
def renderizza(content_raw: str) -> str
```

Espande gli shortcode in stile Hugo presenti nel testo.

Punto di ingresso del package: istanzia un processore e gli
delega l'elaborazione del Markdown grezzo.

Args:
    content_raw: testo Markdown grezzo con gli shortcode.

Returns:
    Testo con gli shortcode espansi in HTML.

## `sitekit.shortcodes.attributi`

File: `src/sitekit/shortcodes/attributi.py`

- `api_sha256`: `65543927f106a69572dcf0d742db025e46defcc791591a76b33bf27b1f6c1d5a`
- `file_sha256`: `f9c5a46620670eae5a78523e9f83adfa07ee4600dfa4a6ad6a406023c132ce93`

**Funzioni**

```python
def analizza_attributi(testo: str) -> dict[str, str]
```

Estrae le coppie chiave="valore" dalla parte attributi di
uno shortcode.

Accetta sia virgolette doppie sia singole. Una stringa vuota
o priva di attributi produce un dizionario vuoto.

Args:
    testo: porzione di shortcode con gli attributi, ad
        esempio 'url="/img.jpg" alt="Gigetto"'.

Returns:
    Dizionario degli attributi trovati, nell'ordine di
    comparsa.

## `sitekit.shortcodes.filtri`

File: `src/sitekit/shortcodes/filtri.py`

- `api_sha256`: `42b86ed821e4f5ecc057a083db42aad477a4547b29fd5c8c3a2110f2f031fcd7`
- `file_sha256`: `dc606b89e6332d8749f9bf779ee919400b6ed01df3524a45361c7498caee001e`

**Funzioni**

```python
def asset(percorso: str) -> str
```

Risolve un percorso relativo rispetto alla cartella assets.

Vale per qualsiasi risorsa servita da assets (immagini, audio,
video, css, javascript, font). Gli URL assoluti (http, https o
protocol-relative) vengono restituiti invariati.

Args:
    percorso: percorso della risorsa relativo alla radice degli
        asset, ad esempio "images/immagine/immagine__800.jpg".

Returns:
    URL completo con il prefisso ASSETS_URL, ad esempio
    "/assets/images/immagine/immagine__800.jpg".

## `sitekit.shortcodes.processore`

File: `src/sitekit/shortcodes/processore.py`

- `api_sha256`: `9e166bd4274475f529a9e91dc6c42bc24e1200eaff1c4dd7c4c8d9323280becb`
- `file_sha256`: `fdbef6ee32cc3b61ed46e7b0f0fefac7e716b65a42f407fe965f63f3eedc2255`

### `class ProcessoreShortcode`

Espande shortcode in stile Hugo nel testo Markdown grezzo.

Riconosce due delimitatori: {{< ... >}} passa il contenuto
interno così com'è, mentre {{% ... %}} lo converte prima da
Markdown a HTML. Ogni delimitatore esiste in forma accoppiata
chiusa da un tag "end" e in forma auto-chiusa con il
marcatore "/" finale (".../>}}" o ".../%}}"), che non
richiede "end". Ogni shortcode viene reso dal template Jinja2
omonimo presente in PLUGINS_DIR.

**Metodi**

```python
def __init__(self) -> None
```

```python
def processa(self, content_raw: str) -> str
```

Sostituisce tutti gli shortcode con l'HTML renderizzato.

Le forme accoppiate vengono elaborate prima di quelle
singole, così che un tag di apertura di una coppia non
venga scambiato per uno shortcode singolo.

Args:
    content_raw: testo Markdown grezzo con gli shortcode.

Returns:
    Testo con gli shortcode espansi in HTML.

## `sitekit.shortcodes.scoperta`

File: `src/sitekit/shortcodes/scoperta.py`

- `api_sha256`: `bfbdc276f62ab315cd10f35b4af386e06e4ad5a08771fc13ecac119c0060bdcb`
- `file_sha256`: `cc9483893757eb57bbf79a44bce9aa44125e32170ea62124fd9d3fc448dab904`

**Funzioni**

```python
def percorsi_template(input_file: Path) -> list[Path]
```

Trova i template usati dagli shortcode inline di un file.

Serve alla cache: includendo questi template nel digest, la
chiave cambia quando uno di essi viene modificato. I template
inesistenti vengono ignorati, coerentemente con il rendering
tollerante del processore.

Args:
    input_file: Path del file Markdown da analizzare.

Returns:
    Lista di Path ai template degli shortcode, senza
    duplicati, nell'ordine di prima comparsa.

## `sitekit.shortcuts`

File: `src/sitekit/shortcuts/__init__.py`

- `api_sha256`: `fd445c07308830e62b937f60e282290ad80941d2d822689c3c618fe1c63055cd`
- `file_sha256`: `33426ee6e70b8a897fc22fac96d91190052147b40dda3c3aeedeb11473eb6b98`

**Nomi riesposti da questo package**

- `content (da )`
- `i18n (da )`

## `sitekit.shortcuts.content`

File: `src/sitekit/shortcuts/content.py`

- `api_sha256`: `aa7eaf3e360b17a112b91007a9e8995b009ab857ec2a110290fe75a17e1cae41`
- `file_sha256`: `1a748770b4f5fb08866ec5bc799eb3a16e5628c905ba92413398bae08d6e4345`

**Funzioni**

```python
def load(*path: str | Path) -> dict | None
```

Shortcut di sitekit.cache.load per caricare
un file di configurazione dalla cartella content
predefinita.

Accetta stringhe e istanze di Path. Se viene passata una Path
assoluta, viene usata direttamente senza prefissare CONTENT_DIR.

## `sitekit.shortcuts.i18n`

File: `src/sitekit/shortcuts/i18n.py`

- `api_sha256`: `ad546bd986c68c2f2b112264c49c70a8c9b2d0faeadaf3a6d5b0e2275e1213c1`
- `file_sha256`: `1ba2acde9cf2d440b75a56ac712bf9edd30889df4e57f3211f7530aa6e30509a`

**Funzioni**

```python
def load(*path: str) -> dict | None
```

Shortcut di sitekit.cache.load per caricare
un file di configurazione dalla cartella i18n
predefinita

## `sitekit.sitemap`

File: `src/sitekit/sitemap/__init__.py`

- `api_sha256`: `a43e39cf265cbf8fd7cf57a51b332a768310c929c4d8258d11a2b52b048f461d`
- `file_sha256`: `0c36b37a0d3ef1d1778821853a22d12fb45384a550dcf111f0a9a886c17a85ff`

**Nomi riesposti da questo package**

- `datetime (da datetime)`
- `urljoin (da urllib.parse)`
- `escape (da xml.sax.saxutils)`
- `settings (da sitekit.settings)`

**Funzioni**

```python
def add(url: str, alternate_url: str = None, locale: str = None, change_freq: str = 'monthly', priority: float = None)
```

```python
def generate()
```

## Manifesto impronte

```json
{
  "package": "sitekit",
  "version": "",
  "generated": "2026-08-05",
  "modules": {
    "sitekit": {
      "path": "src/sitekit/__init__.py",
      "file_sha256": "cd3ff431472608ad96aa9d18537bb7d1087b7f60c265f34390ab43b9afa4ff5f",
      "api_sha256": "1aef9256b064c15c2d37af9e34eb5bd0d9da269fa947e24607dc0e86710c7527"
    },
    "sitekit.assets": {
      "path": "src/sitekit/assets/__init__.py",
      "file_sha256": "c4d61aca7690d5d6ed6166bd8ed92e75d386cbb7bec52e700fae923dbc9241f2",
      "api_sha256": "d3ad19ff54239ab2de956d22cc7f189ba4a9ff55af75c8a5d495dd9081984d88"
    },
    "sitekit.assets.costruzione": {
      "path": "src/sitekit/assets/costruzione.py",
      "file_sha256": "4cc4c77e6ae477943b38714746c82745fcee975d2142aee173705b791f86dd6c",
      "api_sha256": "c92240c66cc40a60aef6dd95456cd6cf1d657421fdd841a1668258c1d7bd1681"
    },
    "sitekit.assets.percorsi": {
      "path": "src/sitekit/assets/percorsi.py",
      "file_sha256": "ecaa704dae38a965c2da1021e960ae5136670d95b187536f8a996506e8a618a4",
      "api_sha256": "37ca1b03ac5ce093228c7aa52e7922fb3982530be180cc836f6e7721a5363000"
    },
    "sitekit.cache": {
      "path": "src/sitekit/cache/__init__.py",
      "file_sha256": "2748c075de5a0f4f55c616401c558d2a2206112ad64b8a6f8277f9c10f8be5ef",
      "api_sha256": "890d690ab049c52fef0de3c2ea895102ca87d1f1a7c0a8b843834f7498255a1b"
    },
    "sitekit.cache.ram": {
      "path": "src/sitekit/cache/ram.py",
      "file_sha256": "c82c90b05fa8639b0533fa8dc019e6d75fcbd7549e1168b49c9bbf465a2b9bfc",
      "api_sha256": "8dc87f5117648857f3b7bbdf0161b1880c4bc120490196bec22e5328f21b6713"
    },
    "sitekit.configurazioni": {
      "path": "src/sitekit/configurazioni/__init__.py",
      "file_sha256": "bdcc259194b43785be5674f5de53642d5f0d7ca0f2f45ea6ea504f8bd3b57a76",
      "api_sha256": "c7fe2c8f4dc284fa7e38775ece694cc4792f895169ba7b6641dbdc2f31db4001"
    },
    "sitekit.configurazioni.descrizioni": {
      "path": "src/sitekit/configurazioni/descrizioni/__init__.py",
      "file_sha256": "96127530152bbd5fa0b609f5c4da3487065bb440883945e01a1c7cb43101c7e4",
      "api_sha256": "8c58c8968a20f3fb3696288fc4be8545b724a078045fc1cc8051e0472306cd7e"
    },
    "sitekit.configurazioni.images": {
      "path": "src/sitekit/configurazioni/images.py",
      "file_sha256": "9e7780f9a3ffad7e03a534c195a7311bbf22ca66a0b6b2dd85f4d38f803fe43a",
      "api_sha256": "0297c7887d76b9fe874d6375e7e71230858a41970705e7fa4cc276529d3351cb"
    },
    "sitekit.configurazioni.imgcache": {
      "path": "src/sitekit/configurazioni/imgcache.py",
      "file_sha256": "7b6b8003f9406ef0c3177cef0deae36d01f3e3bd63551159401d9629c756bc5d",
      "api_sha256": "c78e2fd7167a97fcd86118e4b7ec2d4bfda497a018d7b6b406b30ad66f30a64f"
    },
    "sitekit.images": {
      "path": "src/sitekit/images/__init__.py",
      "file_sha256": "5cdc4a1519353747b64f4504cd2adca60218514a0d3a45d988cd529b902934ba",
      "api_sha256": "ff059c280cabeb4f2888629a353c7e8051af90bae5d910970e3244fbc13bfc05"
    },
    "sitekit.images.images": {
      "path": "src/sitekit/images/images.py",
      "file_sha256": "df67bdedf40248ee4751502d64e72ea14544474245dde1cc4b2169feb6e8b209",
      "api_sha256": "339a9ab3dd98e357f10fae8bf89c405d88096e2b33e726b279413343439f8640"
    },
    "sitekit.images.imgcache": {
      "path": "src/sitekit/images/imgcache.py",
      "file_sha256": "a1c2509c1e6196c8b4281f28aa85515bae23bf14256989af9ca090b9408627c8",
      "api_sha256": "3b1eb946b805471b2aa7518cf71f8407b5107bcfde11de6bdb3e17617d0ac943"
    },
    "sitekit.images.picture_class": {
      "path": "src/sitekit/images/picture_class.py",
      "file_sha256": "5805d29f409e8e41777a2f66776f081b0b9694a3537ef841db3b71b7e17ba4ef",
      "api_sha256": "4b843e3658dd066c8639b6469abf7a517f90cca9a6f8714026e05d202786e3d3"
    },
    "sitekit.jsonld": {
      "path": "src/sitekit/jsonld/__init__.py",
      "file_sha256": "bb5a79bdb003cb843aa59090b57e0c9c0ee1dc4620c84b551eeabbc2f15b3437",
      "api_sha256": "784d114313fb81362ac8bf282a8246ad430f0fb5df8ca282af152bd28a67d6f3"
    },
    "sitekit.jsonld.menu": {
      "path": "src/sitekit/jsonld/menu.py",
      "file_sha256": "49dc5e601b317d1b1d478b3d1bf8a50f8345b092f3a48d1796266f3adecd6c8e",
      "api_sha256": "350b90329c6f6197076427231c38a7a9490144e74e0b9a1dc782dab245e6365a"
    },
    "sitekit.jsonld.schema": {
      "path": "src/sitekit/jsonld/schema.py",
      "file_sha256": "7be792788c843cf5e2f00a1669d5e9de1128b3a2740dec029ba442cd63285b7b",
      "api_sha256": "31da952caea594d96c173b372342b93e8764f8aece30b85e59e5f7d89ec55b52"
    },
    "sitekit.localize": {
      "path": "src/sitekit/localize/__init__.py",
      "file_sha256": "56f9d6bef586bc8070ae58a3a185184e2dc8e026b21cd875a35c05d6c97fbf89",
      "api_sha256": "a32940845b92d7eb38d812f6e86fcb3f216002955f4e3929adde87fd2ec9f81e"
    },
    "sitekit.memos": {
      "path": "src/sitekit/memos/__init__.py",
      "file_sha256": "c36135e2015b2dbb15ef0b6169743c56aade30a6d4b00a772d7441a7d2d632e0",
      "api_sha256": "ae17689cb565bc44f907ea9e9e1c269cd5b49c00badec06f3f1d942c6bb56ae4"
    },
    "sitekit.openings": {
      "path": "src/sitekit/openings/__init__.py",
      "file_sha256": "b944a053cd564cef06f3d9aef7ec8c46637a58f2f781954e8eae9d0771d5afcb",
      "api_sha256": "7a20a6de024cdf5284977f9f04ee09f83da49ab6d7be4fb518ce9295b8675e02"
    },
    "sitekit.openings.classes": {
      "path": "src/sitekit/openings/classes/__init__.py",
      "file_sha256": "fbd99057d62e8886a399967712620358e13a3033b5ea776db8bdf60bc8e70069",
      "api_sha256": "2c578d3e3e6a5b114c1e71f7ad617330ea0ce03d2131c21b4e9e9c3bb3400a59"
    },
    "sitekit.openings.classes.dayopeningclass": {
      "path": "src/sitekit/openings/classes/dayopeningclass.py",
      "file_sha256": "090067fd8bcca0fdf4d73ad6b0d353205fc153bea180e9d6f44b133b7754a762",
      "api_sha256": "c5a5dca11da2544daae5aa0920a312aa45a8b8718a059b0706b9f2446f930bc4"
    },
    "sitekit.openings.classes.holidayclass": {
      "path": "src/sitekit/openings/classes/holidayclass.py",
      "file_sha256": "b732b48e7f386c3b7547225f0d024010480122e05a069c38e91e09c86ba7568a",
      "api_sha256": "0687d659b92039225421c9127895e91cbf622ec7f5b16ba44d8d5c91baab6ed3"
    },
    "sitekit.openings.classes.holidaylistclass": {
      "path": "src/sitekit/openings/classes/holidaylistclass.py",
      "file_sha256": "70fc78fe9cf08598eff3b55d05bd1ee03aec60abbf57283b88eaebb218af08a1",
      "api_sha256": "1a68890633ca457fa8af9a19b46032ee7d1e3e6f374baf9fdf247706c6510e4a"
    },
    "sitekit.openings.classes.openingsclass": {
      "path": "src/sitekit/openings/classes/openingsclass.py",
      "file_sha256": "9a80b0c3f86a3c5dee9ef2a1b5b6cfa2b09c8fe38b5a5b76647730b921d7687e",
      "api_sha256": "060ba3bb731602bc28ac7bb9318cc69b6fcf1ff4efd9c16c057350b61c05c83f"
    },
    "sitekit.openings.classes.turnclass": {
      "path": "src/sitekit/openings/classes/turnclass.py",
      "file_sha256": "fab77eb109a9df6be3bdda16e1d6fc5bc1f7257ee1459d44e3ffc71d52d87d08",
      "api_sha256": "d50276826b9e56f3de60dfdba6def0806086a4b54d6d7d8de213cdbd3e14360c"
    },
    "sitekit.pagebundle": {
      "path": "src/sitekit/pagebundle/__init__.py",
      "file_sha256": "6ae67749faebfe23a134c3a6f4fc348b6f81ede3a196f02a890e02d9473ecabf",
      "api_sha256": "99ac4ba347e5dc2ae4953763235fca6bfb16d58b2926d700aba735052c8ca901"
    },
    "sitekit.pagebundle.media": {
      "path": "src/sitekit/pagebundle/media.py",
      "file_sha256": "aee22b98516086064c22e77e56f847440fa48bc636fe7ccfe073af426d989f9b",
      "api_sha256": "cd33d814895402cf573ceda3f6a1abc7bde6925a260725204939a881b8721d31"
    },
    "sitekit.pagebundle.nomi": {
      "path": "src/sitekit/pagebundle/nomi.py",
      "file_sha256": "252f281fd8de6299d4aeb8795b954d566b24ffe06edc75831c019ac29117b6f3",
      "api_sha256": "c14ced8cd6d72b634f9e700b78997b2a1b156da58e385f43dffe377251b85ee9"
    },
    "sitekit.privacy": {
      "path": "src/sitekit/privacy/__init__.py",
      "file_sha256": "af823c1378e492d48acced3b03357c73d0caeed6a523f48765b49d73909339ba",
      "api_sha256": "3e5f924d5f5befb1e940061a4c583f9a8a43bb5a435cd7c5981437c89884fc01"
    },
    "sitekit.robots": {
      "path": "src/sitekit/robots/__init__.py",
      "file_sha256": "50eb4436aa177c05b43d3a69aee7013d1529832202c42c162852edb677034576",
      "api_sha256": "cf7d1fd7a07641b33d1ec8e87eb70574ddbaf48faae3599e4b45090a916170ae"
    },
    "sitekit.router": {
      "path": "src/sitekit/router/__init__.py",
      "file_sha256": "233c645b8dfdd3dfd3135c201680551150a30c8e8561650ec3a0609e2d2d6a8c",
      "api_sha256": "6800513c8678a3430bf1eb4786b47e6e012a463f27f4dc951572fe49ef9dc2f6"
    },
    "sitekit.router.router": {
      "path": "src/sitekit/router/router.py",
      "file_sha256": "3ae9dc97904713e30e13281289d7f16c5860d25550d4306d63d7b8e34782ba57",
      "api_sha256": "87c4c604f79efe709e67f2fdd2b2b902b9b2eff230f829d9b4a40086b41c105d"
    },
    "sitekit.rssreader": {
      "path": "src/sitekit/rssreader/__init__.py",
      "file_sha256": "d45dc361af653458a63ba3806f887c769f0dea254bf75237c51742dad699647f",
      "api_sha256": "20a734ed3ebb18c9d96e3850224f210c361201f2529a620ecc196d9806ece118"
    },
    "sitekit.rssreader.memos": {
      "path": "src/sitekit/rssreader/memos.py",
      "file_sha256": "d1ee4150e4915f99550467e233425898eef0314827e9f54b796d173916decf9e",
      "api_sha256": "92e3f95d9be5198b8d0c6b0473042c9818885e2dd8ad98e7ca08cd537b20e262"
    },
    "sitekit.rssreader.wordpress": {
      "path": "src/sitekit/rssreader/wordpress.py",
      "file_sha256": "38c0367a69247d49c9a79dab51982d928043d0a96a9099ff10e17a65a8877833",
      "api_sha256": "502127c44ce28ed46e272a2aa670e908d74396001955ae461784a186ab15c42d"
    },
    "sitekit.settings": {
      "path": "src/sitekit/settings.py",
      "file_sha256": "f5b07ff3c615801794d8f6724976162be1f12c1eccabfec151ec17e89bbd6d1f",
      "api_sha256": "9b4ff52367ed1de06c0fb81aaae97e0f62b36bd4c79c49c28539fcfef5f3f511"
    },
    "sitekit.shortcodes": {
      "path": "src/sitekit/shortcodes/__init__.py",
      "file_sha256": "9a19f0e32b96567265b7b660d3ea0b5296d70890b7561750dd2bffc0cf7c2d8c",
      "api_sha256": "06cd0408d47dd823306a2bd5e3bc08bdece5f32dd53ae0c1a109c755fe8de374"
    },
    "sitekit.shortcodes.attributi": {
      "path": "src/sitekit/shortcodes/attributi.py",
      "file_sha256": "f9c5a46620670eae5a78523e9f83adfa07ee4600dfa4a6ad6a406023c132ce93",
      "api_sha256": "65543927f106a69572dcf0d742db025e46defcc791591a76b33bf27b1f6c1d5a"
    },
    "sitekit.shortcodes.filtri": {
      "path": "src/sitekit/shortcodes/filtri.py",
      "file_sha256": "dc606b89e6332d8749f9bf779ee919400b6ed01df3524a45361c7498caee001e",
      "api_sha256": "42b86ed821e4f5ecc057a083db42aad477a4547b29fd5c8c3a2110f2f031fcd7"
    },
    "sitekit.shortcodes.processore": {
      "path": "src/sitekit/shortcodes/processore.py",
      "file_sha256": "fdbef6ee32cc3b61ed46e7b0f0fefac7e716b65a42f407fe965f63f3eedc2255",
      "api_sha256": "9e166bd4274475f529a9e91dc6c42bc24e1200eaff1c4dd7c4c8d9323280becb"
    },
    "sitekit.shortcodes.scoperta": {
      "path": "src/sitekit/shortcodes/scoperta.py",
      "file_sha256": "cc9483893757eb57bbf79a44bce9aa44125e32170ea62124fd9d3fc448dab904",
      "api_sha256": "bfbdc276f62ab315cd10f35b4af386e06e4ad5a08771fc13ecac119c0060bdcb"
    },
    "sitekit.shortcuts": {
      "path": "src/sitekit/shortcuts/__init__.py",
      "file_sha256": "33426ee6e70b8a897fc22fac96d91190052147b40dda3c3aeedeb11473eb6b98",
      "api_sha256": "fd445c07308830e62b937f60e282290ad80941d2d822689c3c618fe1c63055cd"
    },
    "sitekit.shortcuts.content": {
      "path": "src/sitekit/shortcuts/content.py",
      "file_sha256": "1a748770b4f5fb08866ec5bc799eb3a16e5628c905ba92413398bae08d6e4345",
      "api_sha256": "aa7eaf3e360b17a112b91007a9e8995b009ab857ec2a110290fe75a17e1cae41"
    },
    "sitekit.shortcuts.i18n": {
      "path": "src/sitekit/shortcuts/i18n.py",
      "file_sha256": "1ba2acde9cf2d440b75a56ac712bf9edd30889df4e57f3211f7530aa6e30509a",
      "api_sha256": "ad546bd986c68c2f2b112264c49c70a8c9b2d0faeadaf3a6d5b0e2275e1213c1"
    },
    "sitekit.sitemap": {
      "path": "src/sitekit/sitemap/__init__.py",
      "file_sha256": "0c36b37a0d3ef1d1778821853a22d12fb45384a550dcf111f0a9a886c17a85ff",
      "api_sha256": "a43e39cf265cbf8fd7cf57a51b332a768310c929c4d8258d11a2b52b048f461d"
    }
  }
}
```

## Metadata
- Ultima modifica: 2026-08-05
- Modello: claude-opus-5
