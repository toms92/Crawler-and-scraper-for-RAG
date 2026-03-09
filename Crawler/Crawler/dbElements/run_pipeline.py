#!/usr/bin/env python3
"""
Script semplificato per caricare ricette da JSON a ChromaDB
Legge il file JSON e popola il database vettoriale ChromaDB
Configurato per la struttura: Crawler/Crawler/dbElements/
"""

import sys
import json
from datetime import datetime
from pathlib import Path


class RecipesPipeline:
    """Pipeline per caricare ricette da JSON a ChromaDB"""

    def __init__(
            self,
            json_file: str = "itemsExtracted.json",
            chroma_dir: str = None
    ):
        # Usa il path relativo per il JSON (nella stessa directory dello script)
        self.json_file = Path(json_file)
        # Determina dinamicamente la directory per ChromaDB
        if chroma_dir is None:
            docker_root = Path("/app")
            if docker_root.exists():
                # Ambiente Docker
                self.chroma_dir = docker_root / "chroma_db"
            else:
                # Ambiente locale: usa la root del progetto (3 livelli sopra questo file)
                self.chroma_dir = Path(__file__).resolve().parents[3] / "chroma_db"
        else:
            self.chroma_dir = Path(chroma_dir)

        # Crea la directory ChromaDB se non esiste
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Stampa messaggio con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def validate_json(self) -> bool:
        """
        Valida il file JSON

        Returns:
            True se valido, False altrimenti
        """
        self.log(f"Validazione file JSON: {self.json_file}")

        if not self.json_file.exists():
            self.log(f"❌ File JSON non trovato: {self.json_file}", "ERROR")
            self.log(f"   Path assoluto: {self.json_file.absolute()}", "ERROR")
            return False

        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                self.log("❌ Il JSON non contiene una lista", "ERROR")
                return False

            valid_count = sum(1 for item in data if item.get('titolo') and not item.get('errore'))
            total_count = len(data)

            self.log(f"📊 Ricette totali: {total_count}")
            self.log(f"📊 Ricette valide: {valid_count}")
            self.log(f"📊 Ricette con errori: {total_count - valid_count}")

            if valid_count == 0:
                self.log("❌ Nessuna ricetta valida trovata", "ERROR")
                return False

            self.log("✅ File JSON validato")
            return True

        except json.JSONDecodeError as e:
            self.log(f"❌ JSON non valido: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Errore durante la validazione: {e}", "ERROR")
            return False

    def populate_chromadb(self, reset_db: bool = True) -> bool:
        """
        Popola ChromaDB con le ricette dal file JSON

        Args:
            reset_db: Se True, cancella e ricrea il database

        Returns:
            True se successo, False altrimenti
        """
        self.log("Avvio caricamento in ChromaDB...")

        try:
            # Importa e esegui lo script di popolazione
            from populate_chromadb import populate_chromadb

            populate_chromadb(
                json_path=str(self.json_file.absolute()),
                collection_name="ricette",
                persist_directory=str(self.chroma_dir),
                reset_db=reset_db
            )

            self.log("✅ ChromaDB popolato con successo")
            return True

        except Exception as e:
            self.log(f"❌ Errore durante il caricamento: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    def run(self, reset_db: bool = True):
        """
        Esegue la pipeline: valida JSON e carica in ChromaDB

        Args:
            reset_db: Se True, cancella e ricrea il database ChromaDB

        Returns:
            True se successo, False altrimenti
        """
        self.log("=" * 60)
        self.log("CARICAMENTO RICETTE IN CHROMADB")
        self.log(f"Working directory: {Path.cwd()}")
        self.log("=" * 60)

        # Step 1: Validazione JSON
        self.log("\n[STEP 1/2] Validazione file JSON")
        if not self.validate_json():
            self.log("❌ Pipeline interrotta: validazione fallita", "ERROR")
            return False

        # Step 2: Caricamento in ChromaDB
        self.log("\n[STEP 2/2] Caricamento in ChromaDB")
        if not self.populate_chromadb(reset_db=reset_db):
            self.log("❌ Pipeline interrotta: caricamento fallito", "ERROR")
            return False

        self.log("\n" + "=" * 60)
        self.log("✅ CARICAMENTO COMPLETATO CON SUCCESSO")
        self.log("=" * 60)
        return True


def main():
    """Funzione principale"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Carica ricette da JSON a ChromaDB"
    )
    parser.add_argument(
        "--json-file",
        default="itemsExtracted.json",
        help="Nome del file JSON nella directory corrente (default: itemsExtracted.json)"
    )
    parser.add_argument(
        "--chroma-dir",
        default="/app/chroma_db",
        help="Directory per il database ChromaDB (default: /app/chroma_db)"
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Non cancellare il database esistente (aggiungi solo nuovi dati)"
    )

    args = parser.parse_args()

    # Crea ed esegui la pipeline
    pipeline = RecipesPipeline(
        json_file=args.json_file,
        chroma_dir=args.chroma_dir
    )

    success = pipeline.run(reset_db=not args.no_reset)

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()