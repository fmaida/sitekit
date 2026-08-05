# Formato di API-CONTRACT.md

Leggi questo file quando devi modificare il renderer o capire come e' fatto
il documento prodotto.

## Indice

1. Struttura generale del documento
2. Il manifesto delle impronte
3. Rappresentazione canonica per `api_sha256`
4. Integrazione con git e CI

---

## 1. Struttura generale del documento

Il documento e' composto, nell'ordine, da:

1. **Titolo** — `# API Contract — <nome pacchetto>`
2. **Nota di intestazione** — avverte che il file e' generato, spiega a chi
   e' destinato e rimanda a `CLAUDE.md` per le convenzioni interne
3. **Descrizione e versione** — presi da `pyproject.toml`
4. **Verifica di validita'** — il comando `--check` da eseguire prima di
   fidarsi del contenuto
5. **Indice dei moduli** — tabella con impronte troncate a 16 caratteri
6. **Una sezione per modulo** — costanti, funzioni, classi
7. **Manifesto impronte** — blocco JSON leggibile dalla macchina
8. **Metadata** — data e modello, secondo la convenzione dei `CLAUDE.md`

L'ordine non e' casuale: la verifica sta **prima** del contenuto, cosi' un
agente che legge dall'alto incontra l'istruzione di controllo prima di
assorbire dati potenzialmente obsoleti.

## 2. Il manifesto delle impronte

Il blocco JSON in fondo e' la fonte di verita' per `--check`. Viene
riletto con una espressione regolare che cerca l'intestazione
`## Manifesto impronte` seguita da un blocco recintato `json`.

```json
{
  "package": "nome-pacchetto",
  "version": "0.3.1",
  "generated": "2026-08-04",
  "modules": {
    "pacchetto.modulo": {
      "path": "src/pacchetto/modulo.py",
      "file_sha256": "...",
      "api_sha256": "..."
    }
  }
}
```

La tabella dell'indice mostra le impronte troncate perche' servono all'occhio
umano; il confronto automatico usa sempre il manifesto completo.

## 3. Rappresentazione canonica per `api_sha256`

L'impronta dell'API non e' calcolata sul markdown prodotto, ma su una
rappresentazione canonica intermedia costruita in `hasher.py`. Questo e'
importante: se l'impronta dipendesse dal markdown, ogni ritocco estetico al
renderer invaliderebbe tutti i contratti esistenti.

Ogni elemento diventa una riga con un prefisso che ne dichiara la natura:

```
module:pacchetto.modulo
doc:module:<docstring normalizzata su una riga>
reexport:<nome> (da <origine>)
const:<NOME>:<annotazione>=<valore>
fn:<nome>(<par>:<tipo>=<default>,...)-><ritorno>|<flag>
doc:<nome>:<docstring normalizzata>
class:<Nome>(<basi>)
attr:<Classe>.<attributo>:<annotazione>=<default>
fn:<Classe>.<metodo>(...)-><ritorno>|<flag>
```

Le righe vengono poi **ordinate alfabeticamente** prima di essere unite e
sottoposte a hash. Cosi' spostare una funzione piu' in alto nel file non
produce un falso allarme: il contratto non e' cambiato davvero.

Gli spazi nelle docstring sono normalizzati con `" ".join(testo.split())`,
quindi riformattare una docstring senza cambiarne le parole non invalida
l'impronta. Cambiarne le parole si': una docstring e' parte del contratto
per un lettore IA, perche' e' li' che sta descritto il comportamento.

I flag in coda alla firma codificano `is_async`, `is_property` e
`is_static`, perche' trasformare un metodo in proprieta' cambia il modo in
cui il consumatore lo usa.

## 4. Integrazione con git e CI

`--check` esce con codice `1` quando il documento e' disallineato. Si presta
a un hook pre-commit:

```bash
#!/bin/sh
python scripts/generate_contract.py . --check || {
    echo "API-CONTRACT.md non allineato: rigeneralo prima del commit."
    exit 1
}
```

Il modo migliore di usarlo pero' non e' bloccare il commit ma **rigenerare
automaticamente** e aggiungere il file al commit in corso, cosi' il contratto
resta allineato per costruzione invece che per disciplina.

Nota che `file_sha256` diverso con `api_sha256` uguale non e' un errore: lo
script lo segnala come informazione e restituisce comunque `0`.
