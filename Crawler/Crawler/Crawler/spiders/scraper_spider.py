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


def estrai_tag_dietetici(html_content):
    """
    Estrae i tag dietetici dalla pagina HTML (vegetariano, senza glutine, ecc.)
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova il container dei tag dietetici
    container = soup.find('div', class_='gz-list-featured-data-other')

    if not container:
        return None

    # Trova tutti i tag con classe gz-name-featured-data-other
    tag_elements = container.find_all('span', class_='gz-name-featured-data-other')

    tag_dietetici = []

    for tag in tag_elements:
        nome_tag = tag.get_text(strip=True)
        if nome_tag:
            tag_dietetici.append(nome_tag)

    return tag_dietetici if tag_dietetici else None

def estrai_ingredienti(html_content):
    """
    Estrae gli ingredienti dalla pagina HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova tutti gli elementi <dd> con classe gz-ingredient
    ingredienti_items = soup.find_all('dd', class_='gz-ingredient')

    ingredienti = []

    for item in ingredienti_items:
        # Estrai il nome dell'ingrediente (dentro il tag <a>)
        name_tag = item.find('a')
        nome = name_tag.get_text(strip=True) if name_tag else None

        # Estrai la quantità (dentro il tag <span>)
        quantity_tag = item.find('span')
        if quantity_tag:
            # Pulisci la quantità da newline, tab e spazi multipli
            quantita = quantity_tag.get_text(strip=True)
            # Rimuovi spazi multipli consecutivi
            quantita = ' '.join(quantita.split())
        else:
            quantita = ''

        if nome:
            ingredienti.append({
                'nome': nome,
                'quantita': quantita
            })

    return ingredienti if ingredienti else None

def estrai_macronutrienti(html_content):
    """
    Estrae i macronutrienti dalla pagina HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova tutti gli elementi <li> che contengono i macronutrienti
    macro_items = soup.find_all('li')

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


def estrai_immagine(html_content):
    """
    Estrae l'URL dell'immagine principale della ricetta
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Cerca l'immagine nella meta tag og:image (più affidabile)
    meta_image = soup.find('meta', property='og:image')
    if meta_image and meta_image.get('content'):
        return meta_image.get('content')

    # Alternativa: cerca nell'immagine principale del contenuto
    main_image = soup.find('picture', class_='gz-featured-image')
    if main_image:
        img_tag = main_image.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag.get('src')

    return None


def estrai_tempi(html_content):
    """
    Estrae i tempi di preparazione, cottura e note
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    tempi = {}

    # Trova tutti gli elementi della lista dati ricetta
    data_items = soup.find_all('li', class_='gz-name-featured-data')

    if not data_items:
        # Alternativa: cerca nella sezione gz-recipe-summary
        summary = soup.find('div', class_='gz-recipe-summary')
        if summary:
            data_items = summary.find_all('span', class_='gz-name-featured-data')

    for item in data_items:
        text = item.get_text(strip=True)

        # Preparazione
        if 'Preparazione:' in text:
            strong_tag = item.find('strong')
            if strong_tag:
                tempi['preparazione'] = strong_tag.get_text(strip=True)

        # Cottura
        elif 'Cottura:' in text:
            strong_tag = item.find('strong')
            if strong_tag:
                tempi['cottura'] = strong_tag.get_text(strip=True)

        # Nota (es. "+ 2 ore di riposo")
        elif 'Nota' in text:
            strong_tag = item.find('strong')
            if strong_tag:
                tempi['nota'] = strong_tag.get_text(strip=True)

    return tempi if tempi else None


def estrai_difficolta(html_content):
    """
    Estrae la difficoltà della ricetta (Molto facile, Facile, Media, Difficile, Molto difficile)
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova tutti gli elementi della lista dati ricetta
    data_items = soup.find_all('li')

    for item in data_items:
        text = item.get_text(strip=True)

        # Cerca "Difficoltà:"
        if 'Difficoltà:' in text or 'Difficolta:' in text:
            strong_tag = item.find('strong')
            if strong_tag:
                return strong_tag.get_text(strip=True)

    return None


def estrai_costo(html_content):
    """
    Estrae il costo della ricetta (Basso, Medio, Elevato)
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova tutti gli elementi della lista dati ricetta
    data_items = soup.find_all('li')

    for item in data_items:
        text = item.get_text(strip=True)

        # Cerca "Costo:"
        if 'Costo:' in text:
            strong_tag = item.find('strong')
            if strong_tag:
                return strong_tag.get_text(strip=True)

    return None


def estrai_dosi(html_content):
    """
    Estrae le dosi/porzioni della ricetta
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova tutti gli elementi della lista dati ricetta
    data_items = soup.find_all('li')

    for item in data_items:
        text = item.get_text(strip=True)

        # Cerca "Dosi per:"
        if 'Dosi per:' in text:
            strong_tag = item.find('strong')
            if strong_tag:
                return strong_tag.get_text(strip=True)

    return None


def estrai_categoria(html_content):
    """
    Estrae la categoria della ricetta (es. Dolci, Primi, Secondi)
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Cerca nel breadcrumb
    breadcrumb = soup.find('div', class_='gz-breadcrumb')
    if breadcrumb:
        # Trova il primo link (che di solito è la categoria principale)
        first_link = breadcrumb.find('a')
        if first_link:
            return first_link.get_text(strip=True)

    return None


def scrape_ricetta(url):
    """
    Scarica e processa una singola ricetta
    """
    try:
        # Scarica la pagina
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Estrai tutti i dati (SENZA procedimento)
        titolo = estrai_titolo(response.content)
        macronutrienti = estrai_macronutrienti(response.content)
        ingredienti = estrai_ingredienti(response.content)
        tag_dietetici = estrai_tag_dietetici(response.content)
        immagine = estrai_immagine(response.content)
        tempi = estrai_tempi(response.content)
        difficolta = estrai_difficolta(response.content)
        costo = estrai_costo(response.content)
        dosi = estrai_dosi(response.content)
        categoria = estrai_categoria(response.content)

        return {
            'url': url,
            'titolo': titolo,
            'categoria': categoria,
            'immagine': immagine,
            'difficolta': difficolta,
            'tempi': tempi,
            'costo': costo,
            'dosi': dosi,
            'ingredienti': ingredienti,
            'macronutrienti': macronutrienti,
            'tag_dietetici': tag_dietetici
        }

    except Exception as e:
        print(f"Errore con {url}: {e}")
        return {
            'url': url,
            'titolo': None,
            'categoria': None,
            'immagine': None,
            'difficolta': None,
            'tempi': None,
            'costo': None,
            'dosi': None,
            'ingredienti': None,
            'macronutrienti': None,
            'tag_dietetici': None,
            'errore': str(e)
        }
def scrape_ricetta(url):
    """
    Scarica e processa una singola ricetta
    """
    try:
        # Scarica la pagina
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Estrai tutti i dati (SENZA procedimento)
        titolo = estrai_titolo(response.content)
        macronutrienti = estrai_macronutrienti(response.content)
        ingredienti = estrai_ingredienti(response.content)
        tag_dietetici = estrai_tag_dietetici(response.content)
        immagine = estrai_immagine(response.content)
        tempi = estrai_tempi(response.content)
        difficolta = estrai_difficolta(response.content)
        costo = estrai_costo(response.content)
        dosi = estrai_dosi(response.content)
        categoria = estrai_categoria(response.content)

        return {
            'url': url,
            'titolo': titolo,
            'categoria': categoria,
            'immagine': immagine,
            'difficolta': difficolta,
            'tempi': tempi,
            'costo': costo,
            'dosi': dosi,
            'ingredienti': ingredienti,
            'macronutrienti': macronutrienti,
            'tag_dietetici': tag_dietetici
        }

    except Exception as e:
        print(f"Errore con {url}: {e}")
        return {
            'url': url,
            'titolo': None,
            'categoria': None,
            'immagine': None,
            'difficolta': None,
            'tempi': None,
            'costo': None,
            'dosi': None,
            'ingredienti': None,
            'macronutrienti': None,
            'tag_dietetici': None,
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
    for i, item in enumerate(data, 1):  # [:5] limita a 5 per test
        # Estrai l'URL dall'oggetto
        if isinstance(item, dict) and 'url' in item:
            url = item['url']  # <-- QUI ESTRAE L'URL DALL'OGGETTO
        elif isinstance(item, str):
            url = item
        else:
            print(f"Formato non riconosciuto per l'elemento {i}: {item}")
            continue

        print(f"Processando {i}/5: {url}")
        ricetta = scrape_ricetta(url)
        risultati.append(ricetta)

    # Salva i risultati nel file JSON di output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(risultati, f, ensure_ascii=False, indent=2)

    print(f"\nCompletato! Risultati salvati in {output_file}")


if __name__ == "__main__":
    # Specifica i file di input e output
    input_file = r"C:\Users\tomma\Documents\PythonProjects\CrawlAndScrape\Crawler\Crawler\outputNew\links_finali.json"
    output_file = r"/itemsExtracted.json"

    main(input_file, output_file)