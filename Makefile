.PHONY: help build up down clean crawler load-chromadb all test logs shell

# Colori per output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m # No Color

help: ## Mostra questo messaggio di aiuto
	@echo "$(GREEN)Comandi disponibili:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

build: ## Costruisce l'immagine Docker
	@echo "$(GREEN)Costruzione immagine Docker...$(NC)"
	docker compose build

up: ## Avvia tutti i servizi
	@echo "$(GREEN)Avvio servizi...$(NC)"
	docker compose up

down: ## Ferma tutti i servizi
	@echo "$(GREEN)Arresto servizi...$(NC)"
	docker compose down

clean: ## Rimuove container, volumi e immagini
	@echo "$(YELLOW)⚠️  ATTENZIONE: Questo rimuoverà tutti i dati!$(NC)"
	@read -p "Sei sicuro? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		rm -rf chroma_db/; \
		echo "$(GREEN)Pulizia completata$(NC)"; \
	else \
		echo "$(YELLOW)Operazione annullata$(NC)"; \
	fi

# Comandi specifici

crawler: ## Esegue solo il crawler
	@echo "$(GREEN)Esecuzione crawler...$(NC)"
	docker compose up crawler

load-chromadb: ## Carica JSON in ChromaDB
	@echo "$(GREEN)Caricamento ricette in ChromaDB...$(NC)"
	docker compose --profile chromadb up load-chromadb

all: crawler load-chromadb ## Esegue crawler e poi carica in ChromaDB
	@echo "$(GREEN)✅ Processo completato!$(NC)"

# Comandi di utilità

test: ## Testa il sistema RAG
	@echo "$(GREEN)Test sistema RAG...$(NC)"
	docker compose run --rm --workdir /app/Crawler/Crawler/dbElements crawler python esempio_utilizzo.py

logs: ## Mostra i logs
	docker compose logs -f

logs-crawler: ## Mostra i logs del crawler
	docker compose logs -f crawler

logs-chromadb: ## Mostra i logs del caricamento ChromaDB
	docker compose --profile chromadb logs -f load-chromadb

shell: ## Apre una shell nel container
	docker compose run --rm crawler bash

shell-dbElements: ## Apre una shell nella directory dbElements
	docker compose run --rm --workdir /app/Crawler/Crawler/dbElements crawler bash

python: ## Apre Python interattivo nel container
	docker compose run --rm crawler python

# Comandi di backup e ripristino

backup: ## Crea backup del database ChromaDB
	@echo "$(GREEN)Creazione backup...$(NC)"
	@mkdir -p backup
	@tar -czf backup/chroma_db_$$(date +%Y%m%d_%H%M%S).tar.gz chroma_db/
	@echo "$(GREEN)Backup creato in backup/$(NC)"

list-backups: ## Lista tutti i backup disponibili
	@echo "$(GREEN)Backup disponibili:$(NC)"
	@ls -lh backup/ 2>/dev/null || echo "$(YELLOW)Nessun backup trovato$(NC)"

restore: ## Ripristina da backup (specifica file con FILE=nome_file)
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)Specifica il file di backup con: make restore FILE=backup/nome_file.tar.gz$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Ripristino da $(FILE)...$(NC)"
	@rm -rf chroma_db/
	@tar -xzf $(FILE)
	@echo "$(GREEN)Ripristino completato$(NC)"

# Comandi di monitoraggio

stats: ## Mostra statistiche del database
	@echo "$(GREEN)Statistiche database:$(NC)"
	@docker compose run --rm crawler python -c "import chromadb; client = chromadb.PersistentClient(path='/app/chroma_db'); collection = client.get_collection('ricette'); print(f'Ricette nel database: {collection.count()}')"

size: ## Mostra dimensione del database
	@echo "$(GREEN)Dimensione database ChromaDB:$(NC)"
	@du -sh chroma_db/ 2>/dev/null || echo "$(YELLOW)Database non trovato$(NC)"

check: ## Verifica configurazione
	@echo "$(GREEN)Verifica configurazione...$(NC)"
	@docker compose config

# Workflow completi

first-run: build all ## Prima esecuzione: build + crawler + ChromaDB
	@echo "$(GREEN)✅ Setup completato!$(NC)"
	@echo "$(YELLOW)Esegui 'make test' per testare il sistema$(NC)"

daily-update: crawler load-chromadb backup ## Aggiornamento: crawler + ChromaDB + backup
	@echo "$(GREEN)✅ Aggiornamento completato!$(NC)"

rebuild: clean build all ## Ricostruzione completa: clean + build + all
	@echo "$(GREEN)✅ Ricostruzione completata!$(NC)"

# Sviluppo

dev-crawler: ## Esegue crawler in modalità interattiva
	docker compose run --rm crawler scrapy crawl primo_spyder

lint: ## Verifica codice Python
	docker compose run --rm crawler python -m flake8 . --exclude=venv,__pycache__ || true

# Informazioni

version: ## Mostra versioni software
	@echo "$(GREEN)Versioni:$(NC)"
	@docker compose run --rm crawler python --version
	@docker compose run --rm crawler python -c "import chromadb; print(f'ChromaDB: {chromadb.__version__}')" 2>/dev/null || echo "ChromaDB: non installato"
	@docker compose run --rm crawler python -c "import scrapy; print(f'Scrapy: {scrapy.__version__}')" 2>/dev/null || echo "Scrapy: non installato"

# Debug

check-json: ## Verifica che il file JSON esista
	@echo "$(GREEN)Verifica file JSON...$(NC)"
	@docker compose run --rm --workdir /app/Crawler/Crawler/dbElements crawler ls -lh itemsExtracted.json

check-structure: ## Mostra struttura directory
	@echo "$(GREEN)Struttura directory:$(NC)"
	@docker compose run --rm crawler find /app/Crawler/Crawler/dbElements -type f -name "*.py" -o -name "*.json" | head -20