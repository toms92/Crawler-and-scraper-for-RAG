#!/usr/bin/env python3
"""
Esempio di utilizzo del database vettoriale ChromaDB per ricercare ricette.
Usa la DefaultEmbeddingFunction di ChromaDB (nessuna configurazione necessaria).
- CHROMA_DIR: directory del DB (default: ./chroma_db)
- CHROMA_COLLECTION: nome collection (default: ricette)
"""

import os
import sys
import chromadb
from chromadb.utils import embedding_functions


def main():
    chroma_dir = os.environ.get("CHROMA_DIR", "./chroma_db")
    collection_name = os.environ.get("CHROMA_COLLECTION", "ricette")

    print("=" * 60)
    print("ESEMPIO UTILIZZO CHROMADB - RICERCA RICETTE")
    print("=" * 60)
    print(f"DB: {chroma_dir} | Collection: {collection_name}")
    print("Embedding: DefaultEmbeddingFunction (ChromaDB)\n")

    client = chromadb.PersistentClient(path=chroma_dir)
    ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_collection(name=collection_name, embedding_function=ef)

    # Query interattiva o di esempio
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        queries = [query]
    else:
        queries = [
            "dolce al cioccolato",
            "primo piatto vegetariano",
            "dessert con mascarpone",
        ]

    for q in queries:
        print(f"\n🔍 Query: {q}")
        try:
            res = collection.query(query_texts=[q], n_results=5)
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            ids = res.get("ids", [[]])[0]

            if not docs:
                print("  Nessun risultato")
                continue

            for i, (doc, meta, id_) in enumerate(zip(docs, metas, ids), start=1):
                titolo = meta.get("titolo", "(senza titolo)") if isinstance(meta, dict) else str(meta)
                url = meta.get("url", "-") if isinstance(meta, dict) else "-"
                categoria = meta.get("categoria", "-") if isinstance(meta, dict) else "-"
                print(f"  {i}. {titolo} [id={id_}]")
                print(f"     Categoria: {categoria}")
                print(f"     URL: {url}")
        except Exception as e:
            print(f"  Errore durante la query: {e}")

    print("\nFatto.\n")


if __name__ == "__main__":
    main()
