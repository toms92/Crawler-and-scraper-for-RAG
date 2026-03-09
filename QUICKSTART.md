# 🚀 Quick Start - JSON → ChromaDB Vector DB

Questo progetto ha come scopo primario convertire il file `itemsExtracted.json` in un database vettoriale ChromaDB (versione 0.5.3) da usare in un sistema RAG esterno. Il crawler è stato rimosso.

## 📁 Struttura del Progetto

```
CrawlAndScrape/
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── Makefile
├── chroma_db/                           # Database ChromaDB (auto-creato)
└── Crawler/
    └── Crawler/
        └── dbElements/                   # ← QUI vanno i tuoi script!
            ├── itemsExtracted.json       # File JSON con le ricette (fornito da te)
            ├── run_pipeline.py           # Script di caricamento JSON → ChromaDB
            ├── populate_chromadb.py      # Logica di popolazione e embeddings
            └── esempio_utilizzo.py       # Esempi di ricerca
```

## 📋 Prerequisiti

- Docker e Docker Compose installati
- File Python nella directory `Crawler/Crawler/dbElements/`:
  - `run_pipeline.py`
  - `populate_chromadb.py`
  - `esempio_utilizzo.py`

## 🧠 Embeddings (Default ChromaDB 0.5.3)

Gli embedding vengono generati usando la DefaultEmbeddingFunction di ChromaDB. Non è necessaria alcuna configurazione di provider o modello.

Variabili utili:
- `CHROMA_DIR`: directory del database (default: `./chroma_db`)
- `CHROMA_COLLECTION`: nome della collection (default: `ricette`)
- `RESET_DB`: resetta il DB al primo avvio (`true`/`false`)

## 🎯 Workflow Base

Hai già il file `itemsExtracted.json` in `Crawler/Crawler/dbElements/`. Per convertirlo in un Vector DB ChromaDB:

```powershell
# 1) Build immagine (solo la prima volta)
docker compose build

# 2) Esegui la pipeline JSON → ChromaDB (resetta il DB la prima volta)
docker compose up vectordb
# oppure con Make
make build-vdb
```

Variabili d'ambiente utili (opzionali):
```powershell
$env:CHROMA_DIR = "./chroma_db"                     # path DB
$env:CHROMA_COLLECTION = "ricette"                  # nome collection
$env:RESET_DB = "true"                              # reset alla partenza
```

## 📊 Verifica Risultati

Dopo aver caricato i dati:

```powershell
# Testa una query di esempio
docker compose run --rm --workdir /app/Crawler/Crawler/dbElements vectordb python esempio_utilizzo.py "primo piatto vegetariano"

# Verifica statistiche database
docker compose run --rm vectordb python -c "import chromadb; client = chromadb.PersistentClient(path='/app/chroma_db'); collection = client.get_collection('ricette'); print(f'Ricette: {collection.count()}')"
```

Con Make:
```bash
make test
make stats
```

## 🔧 Posizionamento File

### ✅ Dove mettere i file Python:

```
Crawler/Crawler/dbElements/
├── run_pipeline.py          ← Metti qui
├── populate_chromadb.py     ← Metti qui
├── esempio_utilizzo.py      ← Metti qui
└── itemsExtracted.json      ← Fornito da te (o da altra pipeline esterna)
```

### ✅ Dove viene creato il database:

```
./chroma_db/                 ← ChromaDB (root del progetto)
```

## 🐛 Troubleshooting

### Errore: "can't open file 'run_pipeline.py'"

I file Python devono essere in `Crawler/Crawler/dbElements/`, non nella root!

### Errore: "File JSON non trovato"

Verifica che `itemsExtracted.json` sia in `Crawler/Crawler/dbElements/`:

```powershell
docker compose run --rm --workdir /app/Crawler/Crawler/dbElements vectordb ls -lh itemsExtracted.json
```

### Debug: Verifica struttura

```powershell
# Entra nel container e naviga
docker compose run --rm vectordb bash
cd /app/Crawler/Crawler/dbElements
ls -la
```

## ⚡ Comandi Rapidi

```powershell
# Setup completo
docker compose build

# Costruisci il Vector DB da JSON
docker compose up vectordb

# Test
docker compose run --rm --workdir /app/Crawler/Crawler/dbElements vectordb python esempio_utilizzo.py

# Shell nella directory corretta
docker compose run --rm --workdir /app/Crawler/Crawler/dbElements vectordb bash
```

Con Make:
```bash
make build-vdb    # Build + creazione Vector DB
make test         # Test sistema
make stats        # Statistiche
```

## 💡 Note Importanti

1. **Script Python** → vanno in `Crawler/Crawler/dbElements/`
2. **File JSON** → deve essere presente in `Crawler/Crawler/dbElements/` (fornito da te o da pipeline esterna)
3. **Database ChromaDB** → viene creato in `./chroma_db/` (root del progetto)
4. Il database **persiste** tra i riavvii Docker

## 🎉 Esempio Completo

```powershell
# 1. Posiziona i file Python e il JSON
# Assicurati che questi file siano in: Crawler/Crawler/dbElements/
# - run_pipeline.py
# - populate_chromadb.py
# - esempio_utilizzo.py
# - itemsExtracted.json

# 2. Build immagine
 docker compose build

# 3. Crea il Vector DB (JSON → ChromaDB)
 docker compose up vectordb
 # Se hai modificato i servizi, puoi aggiungere: --remove-orphans
 # docker compose up --remove-orphans vectordb

# 4. Testa una query
 docker compose run --rm --workdir /app/Crawler/Crawler/dbElements vectordb python esempio_utilizzo.py "primo piatto vegetariano"

# 5. Statistiche
 docker compose run --rm vectordb python -c "import chromadb; c=chromadb.PersistentClient(path='/app/chroma_db'); col=c.get_collection('ricette'); print(col.count())"

# Output atteso (esempio):
# 📊 Ricette: 5652
# ✅ Funziona!
```
