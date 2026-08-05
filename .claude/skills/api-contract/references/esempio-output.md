# API Contract — `postino-demo`

> **Documento generato automaticamente. Non modificarlo a mano.**
> Descrive la sola superficie pubblica del pacchetto: firme, tipi e
> docstring. Serve a un agente IA che lavora su un progetto *consumatore*
> di questa libreria e ha bisogno di conoscerne il contratto attuale.
>
> Per le convenzioni di sviluppo interne al pacchetto vedi `CLAUDE.md`.


Spooler di email transazionali su file.

Versione documentata: **0.3.1**

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
| `postino_demo` | `ab11bd4c5fb5bf50` | `60369c9b83354e0d` |
| `postino_demo.sender` | `8a21af86c4d90be7` | `cd5c8e3b1259e7c0` |
| `postino_demo.spooler` | `2d4f559d8ec651a9` | `e5f391eed6482a7d` |

## `postino_demo`

File: `src/postino_demo/__init__.py`

- `api_sha256`: `ab11bd4c5fb5bf50d332515b9ad0e0a4c7fd84c4c0fb28d38b73319bf0fb7cb8`
- `file_sha256`: `60369c9b83354e0df858174f56ff71e2fcc6df123ddc4155b4120bebc941a4e2`

Spooler di email transazionali basato su file markdown.

`__all__`: `send_message`, `Spooler`

**Nomi riesposti da questo package**

- `Spooler (da postino_demo.spooler)`
- `send_message (da postino_demo.sender)`

## `postino_demo.sender`

File: `src/postino_demo/sender.py`

- `api_sha256`: `8a21af86c4d90be7d1e7f0a2be760476053fd45f28f37f6c897819a60c2e266c`
- `file_sha256`: `cd5c8e3b1259e7c0fd6a4bc031cd2a85023f0878f58e04b01e6299dbb101a586`

Invio dei messaggi tramite il provider ZeptoMail.

**Costanti**

- `DEFAULT_TIMEOUT: int` = `30`
- `API_ENDPOINT` = `'https://api.zeptomail.eu/v1.1/email'`

**Funzioni**

```python
def send_message(recipient: str, subject: str, body: str, attachments: list[Path] | None = None, timeout: int = DEFAULT_TIMEOUT, reply_to: str | None = None) -> str
```

Invia un singolo messaggio e restituisce l'identificativo assegnato.

Args:
    recipient: Indirizzo email del destinatario.
    subject: Oggetto del messaggio.
    body: Corpo del messaggio in formato HTML.
    attachments: Allegati opzionali da includere.
    timeout: Secondi di attesa massima per la risposta del provider.

Returns:
    L'identificativo del messaggio accettato dal provider.

Raises:
    DeliveryError: Se il provider rifiuta il messaggio.

## `postino_demo.spooler`

File: `src/postino_demo/spooler.py`

- `api_sha256`: `2d4f559d8ec651a937812cdb800ffebcde3f39ccc31dc9a02d0db7e86271c6d2`
- `file_sha256`: `e5f391eed6482a7d26731e497e0cf381467179ce7431c9534e64f4e7c0015fed`

Gestione della coda di messaggi su filesystem.

### `class Spooler`

Sorveglia una cartella di spool e processa i messaggi in attesa.

**Attributi**

- `queue_path: Path`
- `batch_size: int` = `25`

**Metodi**

```python
def __init__(self, queue_path: Path, batch_size: int = 25) -> None
```

Prepara lo spooler sulla cartella indicata.

Args:
    queue_path: Cartella che contiene i file dei messaggi.
    batch_size: Numero massimo di messaggi processati per ciclo.

```python
def pending(self) -> int
```
*(property)*

Numero di messaggi ancora da inviare.

```python
def flush(self, dry_run: bool = False) -> list[str]
```

Processa i messaggi in coda e restituisce gli identificativi.

Args:
    dry_run: Se vero simula l'invio senza contattare il provider.

Returns:
    Gli identificativi dei messaggi processati.

## Manifesto impronte

```json
{
  "package": "postino-demo",
  "version": "0.3.1",
  "generated": "2026-08-04",
  "modules": {
    "postino_demo": {
      "path": "src/postino_demo/__init__.py",
      "file_sha256": "60369c9b83354e0df858174f56ff71e2fcc6df123ddc4155b4120bebc941a4e2",
      "api_sha256": "ab11bd4c5fb5bf50d332515b9ad0e0a4c7fd84c4c0fb28d38b73319bf0fb7cb8"
    },
    "postino_demo.sender": {
      "path": "src/postino_demo/sender.py",
      "file_sha256": "cd5c8e3b1259e7c0fd6a4bc031cd2a85023f0878f58e04b01e6299dbb101a586",
      "api_sha256": "8a21af86c4d90be7d1e7f0a2be760476053fd45f28f37f6c897819a60c2e266c"
    },
    "postino_demo.spooler": {
      "path": "src/postino_demo/spooler.py",
      "file_sha256": "e5f391eed6482a7d26731e497e0cf381467179ce7431c9534e64f4e7c0015fed",
      "api_sha256": "2d4f559d8ec651a937812cdb800ffebcde3f39ccc31dc9a02d0db7e86271c6d2"
    }
  }
}
```

## Metadata
- Ultima modifica: 2026-08-04
- Modello: Claude Opus 5
