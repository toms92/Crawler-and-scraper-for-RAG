import json
from bs4 import BeautifulSoup
import requests
from pathlib import Path


def estrai_titolo(html_content):
    """
    Estrae il titolo della ricetta dalla pagina HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Cerca il tag h1 con classe gz-title-recipe
    titolo_tag = soup.find('h1', class_='gz-title-recipe')

    if titolo_tag:
        return titolo_tag.get_text(strip=True)
    else:
        return None


def estrai_macronutrienti(html_content):
    """
    Estrae i macronutrienti dalla pagina HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova tutti gli elementi <li> che contengono i macronutrienti
    macro_items = soup.find_all('li', class_=lambda x: x and 'gz-list-macros' in ' '.join(x.split()))

    macronutrienti = {}

    for item in macro_items:
        name_tag = item.find('span', class_='gz-list-macros-name')
        unit_tag = item.find('span', class_='gz-list-macros-unit')
        value_tag = item.find('span', class_='gz-list-macros-value')

        if name_tag and value_tag:
            name = name_tag.get_text(strip=True)
            value = value_tag.get_text(strip=True)
            unit = unit_tag.get_text(strip=True) if unit_tag else ''

            macronutrienti[name] = {
                'valore': value,
                'unita': unit
            }

    return macronutrienti if macronutrienti else None


def scrape_ricetta(url):
    """
    Scarica e processa una singola ricetta
    """
    try:
        # Scarica la pagina
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Estrai i dati
        titolo = estrai_titolo(response.content)
        macronutrienti = estrai_macronutrienti(response.content)

        return {
            'url': url,
            'titolo': titolo,
            'macronutrienti': macronutrienti
        }

    except Exception as e:
        print(f"Errore con {url}: {e}")
        return {
            'url': url,
            'titolo': None,
            'macronutrienti': None,
            'errore': str(e)
        }


def main(input_file, output_file):
    """
    Funzione principale che processa tutti i link
    """
    # Leggi il file JSON di input
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    risultati = []

    # Processa ogni elemento
    for i, item in enumerate(data[:50], 1):
        # Estrai l'URL dall'oggetto
        if isinstance(item, dict) and 'url' in item:
            url = item['url']
        elif isinstance(item, str):
            url = item
        else:
            print(f"Formato non riconosciuto per l'elemento {i}: {item}")
            continue

        print(f"Processando {i}/{len(data)}: {url}")
        ricetta = scrape_ricetta(url)
        risultati.append(ricetta)

    # Salva i risultati nel file JSON di output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(risultati, f, ensure_ascii=False, indent=2)

    print(f"\nCompletato! Risultati salvati in {output_file}")


if __name__ == "__main__":
    # Specifica i file di input e output
    input_file = r"C:\Users\tomma\Documents\PythonProjects\CrawlAndScrape\Crawler\Crawler\outputNew\links_finali.json"  # File con la lista degli URL
    output_file = r"/itemsExtracted.json"  # File con i dati estratti

    main(input_file, output_file)

