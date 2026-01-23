# Usa la versione di Python specifica del progetto
FROM python:3.8.3-slim AS crawler

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia il file dei requisiti e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice
COPY . .

# Comando di default (puoi cambiarlo con il tuo script principale)
CMD ["scrapy", "crawl", "primo_spider"]


