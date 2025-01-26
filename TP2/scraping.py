import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import argparse
import re


# Charger la liste des IDs depuis le fichier CSV et générer les URLs
def charger_urls(csv_file):
    df = pd.read_csv(csv_file)
    base_url = "https://www.trismegistos.org/text/"
    urls = [base_url + str(id).replace("TM", "") for id in df['ID']]
    return urls


def scrap_papyrus(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraction des informations du papyrus
    tm_id = "TM " + url.split('/')[-1]
    date_1 = soup.find('a').text.strip()
    date = soup.find('div', class_='division').text.strip().split(date_1)[-1].strip().replace("Date: ", "")
    #print(date)
    provenance = soup.find('span', text='Provenance:').find_next_sibling('a').text if soup.find('span', text='Provenance:') else None
    language_script = soup.find('span', text='Language/script:').find_next_sibling('a').text if soup.find('span', text='Language/script:') else None
    material = soup.find('span', text='Material:').find_next_sibling('a').text if soup.find('span', text='Material:') else None
    content = soup.find('span', text='Content (beta!):').find_next_sibling(text=True).strip() if soup.find('span', text='Content (beta!):') else None
    publications = ', '.join([pub.text for pub in soup.select('#text-publs p')])
    collections = ', '.join([coll.text for coll in soup.select('#text-coll p')])
    archive = soup.find('div', id='text-arch').get_text(strip=True) if soup.find('div', id='text-arch') else None
    texte_principal = ' '.join([a.text.replace("Papyri.info", "") for a in soup.select('#words-list a')]) if soup.select('#words-list a') else None

    # Extraction des noms de personnes, des noms de lieux et des irrégularités textuelles sous forme de liste de chaînes de caractères et de dictionnaire
    personnes = ', '.join([a.text for a in soup.select('#people-list a')]) if soup.select('#people-list a') else ""
    personnes_liste = personnes.split(", ")
    lieux_cles = ', '.join([a.text for a in soup.select('#places-list a')]) if soup.select('#places-list a') else ""
    lieux_cles_liste = lieux_cles.split(", ")
    #lieux_valeurs_liste = soup.find_all(string=lambda text: text and "getgeo(" in text)
    #print(lieux_valeurs_liste)
    #lieux_valeurs_numerique_liste = [re.sub(r'\D', '', valeur) for valeur in lieux_valeurs_liste]
    #lieux_dico = dict(zip(lieux_cles_liste, lieux_valeurs_numerique_liste))
    # Trouver toutes les chaînes contenant "getgeo(" et extraire l'ID numérique
    getgeo_values_liste = [re.search(r'getgeo\((\d+)\)', item['onclick']).group(1)
                    for item in soup.find_all('li', class_='item-large')
                    if 'onclick' in item.attrs and 'getgeo(' in item['onclick']]
    lieux_dico = dict(zip(lieux_cles_liste, getgeo_values_liste))
    irregularites_textuelles_liste = soup.find_all(string=lambda text: text and ": read " in text)

    # BONUS: Extraction du numéro TM Geo pour capturer le fichier JSON
    provenance_url = soup.find('a', href=lambda x: x and '/place/' in x)
    geo_number = provenance_url['href'].split('/')[-1] if provenance_url else None
    geo_json_url = f'https://www.trismegistos.org/place/{geo_number}' if geo_number else None

    papyrus_data = {
        'ID': tm_id,
        'Date': date,
        'Provenance': provenance,
        'Language/script': language_script,
        'Material': material,
        'Content': content,
        'Publications': publications,
        'Collections': collections,
        'Archive': archive,
        'Texte principal': texte_principal,
        'Personnes': personnes_liste,  # Liste des noms de personnes
        'Lieux': lieux_dico,          # Dictionnaire des noms de lieux et de leur ID de localisation
        'Irrégularités textuelles': irregularites_textuelles_liste, # Liste des irrégularités textuelles
        'TM Geo': geo_number,
        'Geo JSON': geo_json_url
    }

    # Remplacement des valeurs None par "nan" pour s'assurer qu'aucune valeur ne soit vide, afin de faciliter le traitement ultérieur des données
    for key, value in papyrus_data.items():
        if value is None:
            papyrus_data[key] = "nan"

    return papyrus_data


# Fonction principale pour scrapper toutes les pages et sauvegarder dans un fichier CSV
def scraper_total(csv_input, csv_output):
    urls = charger_urls(csv_input)

    # Ouvrir le fichier CSV pour écrire les données avec csv.DictWriter
    with open(csv_output, mode='w', newline='', encoding='utf-8') as file:
        # Entêtes pour le fichier CSV
        headers = [
            'ID', 'Date', 'Provenance', 'Language/script', 'Material', 'Content',
            'Publications', 'Collections', 'Archive', 'Texte principal',
            'Personnes', 'Lieux', 'Irrégularités textuelles', 'TM Geo', 'Geo JSON'
        ]
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        # Scraper chaque URL et écrire les données dans le CSV
        for url in urls:
            print(f"Scraping {url}")
            try:
                papyrus_data = scrap_papyrus(url)
                writer.writerow(papyrus_data)
            except Exception as e:
                print(f"Erreur lors du scraping de {url}: {e}")

    print(f"Scraping terminé. Les données ont été sauvegardées dans '{csv_output}'.")


# Exécuter le programme (exemple d'utilisation : python scraping.py input.csv output.csv)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper les informations des papyri et les stocker dans un fichier CSV.")
    parser.add_argument('csv_input', help="Chemin du fichier d'entrée CSV avec les IDs des papyri")
    parser.add_argument('csv_output', help="Chemin du fichier de sortie CSV pour stocker les données scrapées")
    args = parser.parse_args()

    scraper_total(args.csv_input, args.csv_output)
