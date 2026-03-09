# 🚀 Quick Start - Crawler + ChromaDB

Guida rapida per utilizzare il sistema di crawling e indicizzazione ricette con ChromaDB.

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
        ├── spiders/
        │   └── primo_spyder.py
        └── dbElements/                   # ← QUI vanno i tuoi script!
            ├── itemsExtracted.json       # File JSON con le ricette
            ├── run_pipeline.py           # Script di caricamento
            ├── populate_chromadb.py      # Logica di popolazione
            └── esempio_utilizzo.py       # Esempi di ricerca
```

## 📋 Prerequisiti

- Docker e Docker Compose installati
- File Python nella directory `Crawler/Crawler/dbElements/`:
  - `run_pipeline.py`
  - `populate_chromadb.py`
  - `esempio_utilizzo.py`

## 🎯 Workflow Base

### Scenario 1: Prima Esecuzione (con crawler)

Se non hai ancora estratto le ricette:

```powershell
# 1. Build dell'immagine Docker
docker compose build

# 2. Esegui il crawler per estrarre le ricette
docker compose up crawler

# 3. Carica le ricette in ChromaDB
docker compose --profile chromadb up load-chromadb
```

Con Make:
```bash
make first-run
```

### Scenario 2: Hai già il file JSON

Se hai già `itemsExtracted.json` in `Crawler/Crawler/dbElements/`:

```powershell
# Build (solo la prima volta)
docker compose build

# Carica direttamente in ChromaDB
docker compose --profile chromadb up load-chromadb
```

## 📊 Verifica Risultati

Dopo aver caricato i dati:

```powershell
# Testa il sistema RAG
docker compose run --rm --workdir /app/Crawler/Crawler/dbElements crawler python esempio_utilizzo.py

# Verifica statistiche database
docker compose run --rm crawler python -c "import chromadb; client = chromadb.PersistentClient(path='/app/chroma_db'); collection = client.get_collection('ricette'); print(f'Ricette: {collection.count()}')"
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
└── itemsExtracted.json      ← Creato dal crawler
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
docker compose run --rm --workdir /app/Crawler/Crawler/dbElements crawler ls -lh itemsExtracted.json
```

### Debug: Verifica struttura

```powershell
# Entra nel container e naviga
docker compose run --rm crawler bash
cd /app/Crawler/Crawler/dbElements
ls -la
```

## ⚡ Comandi Rapidi

```powershell
# Setup completo
docker compose build
docker compose up crawler
docker compose --profile chromadb up load-chromadb

# Test
docker compose run --rm --workdir /app/Crawler/Crawler/dbElements crawler python esempio_utilizzo.py

# Shell nella directory corretta
docker compose run --rm --workdir /app/Crawler/Crawler/dbElements crawler bash
```

Con Make:
```bash
make first-run    # Build + crawler + ChromaDB
make test         # Test sistema
make stats        # Statistiche
```

## 💡 Note Importanti

1. **Script Python** → vanno in `Crawler/Crawler/dbElements/`
2. **File JSON** → viene creato in `Crawler/Crawler/dbElements/` dal crawler
3. **Database ChromaDB** → viene creato in `./chroma_db/` (root del progetto)
4. Il database **persiste** tra i riavvii Docker

## 🎉 Esempio Completo

```powershell
# 1. Posiziona i file Python
# Copia run_pipeline.py, populate_chromadb.py, esempio_utilizzo.py
# in: Crawler/Crawler/dbElements/

# 2. Build
docker compose build

# 3. Crawler (se necessario)
docker compose up crawler

# 4. Carica in ChromaDB
docker compose --profile chromadb up load-chromadb

# 5. Testa
docker compose run --rm --workdir /app/Crawler/Crawler/dbElements crawler python esempio_utilizzo.py

# Output:
# 📊 Database contiene 9998 ricette
# ✅ Funziona!
```
