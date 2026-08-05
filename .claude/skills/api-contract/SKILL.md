---
name: api-contract
description: Genera e verifica API-CONTRACT.md, un documento destinato agli agenti IA che descrive la superficie pubblica di un pacchetto Python (firme, tipi, docstring) con impronte sha-256 per rilevare il disallineamento. Usa questa skill ogni volta che l'utente chiede di documentare l'API di una libreria per l'IA, di generare o aggiornare un API-CONTRACT.md, di capire se una dipendenza e' cambiata dall'ultima volta, o quando stai per lavorare su un progetto che consuma una libreria locale e devi conoscerne il contratto attuale. Attiva anche con "contratto API", "documento per l'IA", "README per agenti", "la dipendenza e' cambiata?", "verifica deriva API".
---

# API Contract

Genera `API-CONTRACT.md`: un documento **destinato a un agente IA**, non a un
essere umano, che descrive la superficie pubblica di un pacchetto Python.

## Il problema che risolve

Un agente IA non ha memoria viva del codice. Quando lavora su un progetto che
consuma una libreria locale, o rilegge tutto il sorgente della dipendenza
(costoso e lento), o si fida di quello che ricorda (rischioso: potrebbe essere
obsoleto).

`API-CONTRACT.md` offre una terza via: un contratto compatto e **verificabile**.
Le impronte sha-256 rendono la verifica un fatto oggettivo invece che un atto
di fiducia in una data aggiornata a mano.

## Distinzione dagli altri file di contesto

Tieni chiara questa separazione: sono documenti con pubblici diversi.

| File | Pubblico | Contenuto | Caricamento |
| --- | --- | --- | --- |
| `README.md` | esseri umani | cosa fa il progetto, come si installa | manuale |
| `CLAUDE.md` / `AGENTS.md` | agente che **sviluppa** il pacchetto | convenzioni, comandi di test, struttura | automatico |
| `API-CONTRACT.md` | agente che **consuma** il pacchetto | firme pubbliche, tipi, docstring, impronte | su richiesta |

Il nome `API-CONTRACT.md` e' deliberato: `AGENTS.md` e `CLAUDE.md` vengono
caricati automaticamente e trattati come *istruzioni*. Questo documento e'
invece materiale di *riferimento*, da leggere quando serve. Chiamarlo
`AGENTS.md` lo farebbe iniettare in ogni sessione come se fosse un comando,
sprecando contesto e confondendo dati con direttive.

## Le due impronte

Ogni modulo porta due sha-256, e la differenza fra i due e' il cuore della
skill:

- **`file_sha256`** — l'intero file. Cambia a ogni modifica, anche a un
  commento o a una funzione privata.
- **`api_sha256`** — solo cio' che il documento riproduce davvero: firme,
  annotazioni di tipo, docstring pubbliche, costanti, nomi riesposti. Ignora
  corpi delle funzioni, membri privati, ordine di scrittura e spaziatura.

Se `api_sha256` coincide, la sezione del documento relativa a quel modulo e'
ancora accurata **anche se il file e' cambiato**. Questo evita i falsi allarmi
che renderebbero il documento rumoroso e quindi ignorato.

## Quando rigenerare o verificare

**Verifica** (`--check`) prima di scrivere codice che usa la libreria. Costa
un comando e ti dice se puoi fidarti del documento o devi leggere il sorgente.

**Rigenera** dopo ogni modifica all'API pubblica, nello stesso momento in cui
la fai. Un contratto obsoleto e' peggio di nessun contratto: dava sicurezza
falsa, e l'agente sbaglia con piu' convinzione.

## Uso

Lo script analizza l'AST: **non importa mai i moduli**, quindi non servono le
dipendenze installate e non viene eseguito codice del progetto.

Usa sempre `${CLAUDE_SKILL_DIR}` per raggiungere lo script: la working
directory e' il progetto dell'utente, non la cartella della skill, quindi un
percorso relativo come `scripts/generate_contract.py` non risolve.

```bash
# genera o rigenera il documento
python3 "${CLAUDE_SKILL_DIR}/scripts/generate_contract.py" . \
    --model "<nome modello>"

# verifica la deriva senza riscrivere nulla
python3 "${CLAUDE_SKILL_DIR}/scripts/generate_contract.py" . --check

# analizza una dipendenza che sta altrove
python3 "${CLAUDE_SKILL_DIR}/scripts/generate_contract.py" ../postino --check
```

Il primo argomento e' la radice del progetto da analizzare: puo' essere il
progetto corrente (`.`) oppure una dipendenza in un'altra cartella. Lo script
usa solo la libreria standard, quindi gira con qualunque `python3` >= 3.11
senza installare nulla e senza attivare il virtualenv del progetto.

Il codice di uscita di `--check` e' `0` se allineato, `1` se il contratto e'
cambiato: utile in un hook pre-commit o in CI.

## Scenario tipico in Claude Code

Quando stai per scrivere codice che usa una libreria locale gestita
dall'utente, il primo passo e' verificare il contratto invece di leggere
tutto il sorgente:

1. Cerca un `API-CONTRACT.md` nella radice della dipendenza.
2. Se esiste, lancia `--check` su quella radice.
3. Se il risultato e' `Allineato`, leggi il documento e fidati: hai il
   contratto attuale senza aver aperto un solo file sorgente.
4. Se segnala `API <modulo>`, apri **solo quel modulo**, poi rigenera il
   documento.
5. Se non esiste ancora, proponi all'utente di generarlo.

Opzioni utili:

- `--output <percorso>` — scrive altrove rispetto a `<radice>/API-CONTRACT.md`
- `--model <nome>` — nome del modello registrato nella sezione `## Metadata`

## Come interpretare l'esito di `--check`

| Esito | Significato | Cosa fare |
| --- | --- | --- |
| `Allineato` | il contratto descrive il codice | fidati del documento |
| `interno <modulo>` | cambiati solo dettagli implementativi | il contratto regge, nessuna azione |
| `API <modulo>` | firme, tipi o docstring cambiate | leggi il sorgente **di quel modulo** e rigenera |
| `NUOVO <modulo>` | modulo assente dal documento | rigenera |
| `RIMOSSO <modulo>` | modulo sparito dal codice | rigenera e controlla chi lo importava |

Nota il vantaggio pratico: quando `--check` segnala un problema, ti dice
*quale* modulo rileggere. Non serve ristudiare l'intero pacchetto.

## Collocazione nel repository

`API-CONTRACT.md` vive nella radice del repository della **dipendenza**,
tracciato in git accanto a `CLAUDE.md`.

Non va incluso nel pacchetto distribuito. Con Poetry questo e' gia' il
comportamento predefinito: finche' non lo aggiungi esplicitamente a `include`
in `[tool.poetry]`, non finisce nel wheel e quindi non compare in
`site-packages` del progetto consumatore. Non serve fare nulla di speciale.

Se lo lasciassi finire nel pacchetto installato, un agente che esplora
`site-packages` potrebbe trovarlo e applicarlo fuori contesto a codice che
andrebbe trattato come scatola nera.

## Cosa entra nel documento

Vengono documentati: funzioni e classi pubbliche, metodi pubblici e `__init__`,
proprieta', costanti in MAIUSCOLO, attributi di classe annotati, contenuto di
`__all__` e nomi riesposti dai file `__init__.py`.

Vengono esclusi: nomi che iniziano con `_`, moduli privati, cartelle di test,
`__pycache__`, ambienti virtuali. Se un modulo dichiara `__all__`, quello ha
la precedenza su ogni altra euristica.

## Struttura dei sorgenti

Ogni modulo fa un lavoro solo:

- `scripts/models.py` — strutture dati della superficie pubblica
- `scripts/extractor.py` — analisi AST di un singolo file
- `scripts/discovery.py` — lettura di `pyproject.toml` e scoperta dei moduli
- `scripts/hasher.py` — impronte di file e API
- `scripts/renderer.py` — resa in markdown
- `scripts/generate_contract.py` — interfaccia a riga di comando

Per il dettaglio del formato prodotto vedi `references/formato.md`.

## Metadata
- Ultima modifica: 2026-08-04
- Modello: Claude Opus 5
