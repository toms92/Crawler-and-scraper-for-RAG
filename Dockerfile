# Usa una versione più recente di Python (3.9 è compatibile con il tuo codice)
FROM python:3.9-slim AS crawler

# Imposta la directory di lavoro nel container
WORKDIR /app

# Installa dipendenze di sistema necessarie per ChromaDB
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia il file dei requisiti e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice
COPY . .

# Crea la directory per il database ChromaDB
RUN mkdir -p /app/chroma_db

# Esponi la porta se necessario (opzionale, per future API)
# EXPOSE 8000