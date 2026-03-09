"""
Script per popolare ChromaDB con dati di ricette da file JSON
Questo script crea un database vettoriale per un sistema RAG
"""

import json
import chromadb
from typing import List, Dict, Any, Optional
import os
import shutil

# Embedding functions (ChromaDB 0.5.3)
from chromadb.utils import embedding_functions


def load_json_data(json_path: str) -> List[Dict[str, Any]]:
    """
    Carica i dati dal file JSON
    
    Args:
        json_path: Percorso del file JSON
        
    Returns:
        Lista di dizionari con le ricette
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def filter_valid_recipes(recipes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtra le ricette valide (esclude quelle con errori)
    
    Args:
        recipes: Lista di tutte le ricette
        
    Returns:
        Lista di ricette valide
    """
    valid_recipes = []
    for recipe in recipes:
        # Esclude ricette con errori o senza titolo
        if recipe.get('titolo') and not recipe.get('errore'):
            valid_recipes.append(recipe)
    
    print(f"Ricette totali: {len(recipes)}")
    print(f"Ricette valide: {len(valid_recipes)}")
    print(f"Ricette con errori: {len(recipes) - len(valid_recipes)}")
    
    return valid_recipes


def create_recipe_text(recipe: Dict[str, Any]) -> str:
    """
    Crea una rappresentazione testuale della ricetta per l'embedding
    
    Args:
        recipe: Dizionario con i dati della ricetta
        
    Returns:
        Stringa contenente tutte le informazioni rilevanti della ricetta
    """
    parts = []
    
    # Titolo e categoria
    if recipe.get('titolo'):
        parts.append(f"Titolo: {recipe['titolo']}")
    if recipe.get('categoria'):
        parts.append(f"Categoria: {recipe['categoria']}")
    
    # Difficoltà e tempi
    if recipe.get('difficolta'):
        parts.append(f"Difficoltà: {recipe['difficolta']}")
    if recipe.get('tempi'):
        tempi = recipe['tempi']
        if tempi.get('preparazione'):
            parts.append(f"Tempo di preparazione: {tempi['preparazione']}")
        if tempi.get('cottura'):
            parts.append(f"Tempo di cottura: {tempi['cottura']}")
    
    # Costo e dosi
    if recipe.get('costo'):
        parts.append(f"Costo: {recipe['costo']}")
    if recipe.get('dosi'):
        parts.append(f"Dosi: {recipe['dosi']}")
    
    # Ingredienti
    if recipe.get('ingredienti'):
        ingredienti_list = []
        for ing in recipe['ingredienti']:
            if ing.get('nome'):
                quantita = ing.get('quantita', '')
                ingredienti_list.append(f"{ing['nome']} ({quantita})")
        if ingredienti_list:
            parts.append(f"Ingredienti: {', '.join(ingredienti_list)}")
    
    # Tag dietetici
    if recipe.get('tag_dietetici'):
        parts.append(f"Tag dietetici: {', '.join(recipe['tag_dietetici'])}")
    
    # Macronutrienti (solo i principali)
    if recipe.get('macronutrienti'):
        macro = recipe['macronutrienti']
        macro_str = []
        for key in ['Energia', 'Proteine', 'Carboidrati', 'Grassi']:
            if key in macro and macro[key].get('valore'):
                macro_str.append(f"{key}: {macro[key]['valore']} {macro[key].get('unita', '')}")
        if macro_str:
            parts.append(f"Valori nutrizionali: {', '.join(macro_str)}")
    
    return "\n".join(parts)


def create_recipe_metadata(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea i metadati strutturati per ChromaDB
    
    Args:
        recipe: Dizionario con i dati della ricetta
        
    Returns:
        Dizionario con i metadati
    """
    metadata = {}
    
    # Campi base
    if recipe.get('url'):
        metadata['url'] = recipe['url']
    if recipe.get('titolo'):
        metadata['titolo'] = recipe['titolo']
    if recipe.get('categoria'):
        metadata['categoria'] = recipe['categoria']
    if recipe.get('immagine'):
        metadata['immagine'] = recipe['immagine']
    if recipe.get('difficolta'):
        metadata['difficolta'] = recipe['difficolta']
    if recipe.get('costo'):
        metadata['costo'] = recipe['costo']
    if recipe.get('dosi'):
        metadata['dosi'] = recipe['dosi']
    
    # Tempi
    if recipe.get('tempi'):
        if recipe['tempi'].get('preparazione'):
            metadata['tempo_preparazione'] = recipe['tempi']['preparazione']
        if recipe['tempi'].get('cottura'):
            metadata['tempo_cottura'] = recipe['tempi']['cottura']
    
    # Tag dietetici
    if recipe.get('tag_dietetici'):
        metadata['tag_dietetici'] = ', '.join(recipe['tag_dietetici'])
    
    # Numero di ingredienti
    if recipe.get('ingredienti'):
        metadata['num_ingredienti'] = len(recipe['ingredienti'])
    
    # Calorie
    if recipe.get('macronutrienti') and recipe['macronutrienti'].get('Energia'):
        metadata['calorie'] = recipe['macronutrienti']['Energia'].get('valore', '')
    
    return metadata


def _build_embedding_function():
    """
    Restituisce la DefaultEmbeddingFunction di ChromaDB 0.5.3.
    Non richiede configurazione di provider o modello.
    """
    return embedding_functions.DefaultEmbeddingFunction()


def populate_chromadb(
    json_path: str,
    collection_name: str = "ricette",
    persist_directory: str = "./chroma_db",
    reset_db: bool = False,
):
    """
    Popola ChromaDB con le ricette dal file JSON
    
    Args:
        json_path: Percorso del file JSON
        collection_name: Nome della collection ChromaDB
        persist_directory: Directory dove salvare il database
        reset_db: Se True, elimina e ricrea la collection
    """
    # Verifica versione ChromaDB
    ver = getattr(chromadb, "__version__", None)
    print(f"Versione ChromaDB rilevata: {ver}")
    if ver != "0.5.3":
        raise RuntimeError(f"ChromaDB non è alla versione richiesta: attesa 0.5.3, trovata {ver}")
    
    # Carica i dati
    print("Caricamento dati dal JSON...")
    recipes = load_json_data(json_path)
    
    # Filtra ricette valide
    valid_recipes = filter_valid_recipes(recipes)
    
    if not valid_recipes:
        print("Nessuna ricetta valida trovata!")
        return
    
    # Inizializza ChromaDB
    print(f"\nInizializzazione ChromaDB in: {persist_directory}")
    if reset_db and os.path.exists(persist_directory):
        print(f"Eliminazione directory del database esistente: {persist_directory}")
        try:
            shutil.rmtree(persist_directory, ignore_errors=True)
        except Exception as e:
            print(f"Avviso: impossibile eliminare la directory '{persist_directory}': {e}")
        os.makedirs(persist_directory, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_directory)

    # Costruisci embedding function
    print("Embedding: DefaultEmbeddingFunction (ChromaDB)")
    embedding_function = _build_embedding_function()
    
    # Gestione collection
    try:
        if reset_db:
            print(f"Eliminazione collection esistente: {collection_name}")
            client.delete_collection(name=collection_name)
    except Exception as e:
        # Non bloccare il flusso se la collection non esiste
        print(f"Avviso: impossibile eliminare la collection '{collection_name}': {e}")
    
    # Crea o ottieni la collection
    print(f"Creazione/apertura collection: {collection_name}")
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
        metadata={
            "description": "Database di ricette per sistema RAG",
            "embedding": "DefaultEmbeddingFunction",
        }
    )
    
    # Prepara i dati per ChromaDB
    print("\nPreparazione dati per l'inserimento...")
    documents = []
    metadatas = []
    ids = []
    
    for i, recipe in enumerate(valid_recipes):
        # Crea il testo per l'embedding
        doc_text = create_recipe_text(recipe)
        documents.append(doc_text)
        
        # Crea i metadati
        metadata = create_recipe_metadata(recipe)
        metadatas.append(metadata)
        
        # Crea ID univoco
        recipe_id = f"ricetta_{i}"
        ids.append(recipe_id)
    
    # Inserisci in ChromaDB (in batch)
    print(f"\nInserimento di {len(documents)} ricette in ChromaDB...")
    batch_size = 100
    
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        
        collection.add(
            documents=batch_docs,
            metadatas=batch_meta,
            ids=batch_ids
        )
        print(f"  Inserite {min(i+batch_size, len(documents))}/{len(documents)} ricette")
    
    print("\n✅ Popolamento completato!")
    print(f"Collection '{collection_name}' contiene {collection.count()} documenti")
    
    # Mostra statistiche
    print("\n📊 Statistiche:")
    categorie = {}
    difficolta_count = {}
    
    for recipe in valid_recipes:
        cat = recipe.get('categoria', 'Sconosciuta')
        categorie[cat] = categorie.get(cat, 0) + 1
        
        diff = recipe.get('difficolta', 'Sconosciuta')
        difficolta_count[diff] = difficolta_count.get(diff, 0) + 1
    
    print(f"\nRicette per categoria:")
    for cat, count in sorted(categorie.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {cat}: {count}")
    
    print(f"\nRicette per difficoltà:")
    for diff, count in sorted(difficolta_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {diff}: {count}")


def test_search(
    collection_name: str = "ricette",
    persist_directory: str = "./chroma_db",
):
    """
    Funzione di test per verificare il funzionamento della ricerca
    
    Args:
        collection_name: Nome della collection
        persist_directory: Directory del database
    """
    print("\n" + "="*60)
    print("TEST DI RICERCA")
    print("="*60)
    
    client = chromadb.PersistentClient(path=persist_directory)
    ef = _build_embedding_function()
    collection = client.get_collection(name=collection_name, embedding_function=ef)
    
    # Test query
    test_queries = [
        "ricetta al cioccolato dolce",
        "primo piatto vegetariano",
        "dessert con mascarpone"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        print("Risultati:")
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\n  {i+1}. {metadata.get('titolo', 'N/A')}")
            print(f"     Categoria: {metadata.get('categoria', 'N/A')}")
            print(f"     Difficoltà: {metadata.get('difficolta', 'N/A')}")
            if metadata.get('tag_dietetici'):
                print(f"     Tag: {metadata['tag_dietetici']}")


if __name__ == "__main__":
    # Configurazione
    import os
    JSON_FILE = "itemsExtracted.json"  # percorso relativo alla dir dello script
    COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "ricette")
    DB_DIRECTORY = os.environ.get("CHROMA_DIR", "./chroma_db")

    RESET = os.environ.get("RESET_DB", "true").lower() in {"1", "true", "yes", "y"}
    
    # Popola il database
    populate_chromadb(
        json_path=JSON_FILE,
        collection_name=COLLECTION_NAME,
        persist_directory=DB_DIRECTORY,
        reset_db=RESET,  # Cambia a False se vuoi mantenere dati esistenti
    )
    
    # Esegui test di ricerca
    test_search(
        collection_name=COLLECTION_NAME,
        persist_directory=DB_DIRECTORY,
    )
