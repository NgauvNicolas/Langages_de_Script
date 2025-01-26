import pandas as pd
import argparse
import matplotlib.pyplot as plt
import re
from collections import Counter




def charger_et_nettoyer_dataset(fichier_csv):
    # Charger le fichier CSV dans un DataFrame
    df = pd.read_csv(fichier_csv)

    # Observer les 4 premières lignes
    print("Voici les 4 premières lignes du dataset :")
    print(df.head())

    # Vérification des colonnes vides ou des données manquantes
    print("\nInformations sur le dataset :")
    print(df.info())

    # Compter les textes non capturés (lignes avec NaN dans la colonne 'Full Text')
    textes_non_captures = df[df['Full Text'].isna()].shape[0]
    print(f"\nNombre de textes non capturés pendant le scraping : {textes_non_captures}")

    # Enlever les textes non capturés
    df_cleaned = df.dropna(subset=['Full Text'])

    # Compter le nombre de papyrus après nettoyage
    nombre_papyrus = df_cleaned.shape[0]
    print(f"Nombre de papyrus après nettoyage : {nombre_papyrus}")
    print(df_cleaned)

    # Trier la collection selon l'ID (ordre croissant)
    df_sorted = df_cleaned.sort_values(by='ID')

    return df_sorted



def analyser_genres(df):
    # Extraire le premier mot de la colonne "Content (beta!)" pour déterminer le genre
    df['Genre'] = df['Content (beta!)'].str.split().str[0]

    # Compter les occurrences de chaque genre
    genre_counts = df['Genre'].value_counts()

    # Créer un pie chart pour les genres
    plt.figure(figsize=(8, 6))
    plt.pie(genre_counts, labels=genre_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution des genres de textes')
    plt.axis('equal')  # Pour un pie chart circulaire
    plt.show()


def analyser_reutilisation(df):
    # Compter le nombre de papyrus réutilisés
    reutilises_count = df[df['Publications'].str.contains('reused', na=False)].shape[0]
    print(f"Nombre de papyrus réutilisés : {reutilises_count}")

def analyser_villes(df):
    # Extraire les villes de provenance
    df['Ville'] = df['Provenance'].str.extract(r'([^,]+)')[0]  # Prendre le premier élément avant la virgule

    # Compter les occurrences des villes
    ville_counts = df['Ville'].value_counts()

    # Créer un diagramme en barres pour les villes
    plt.figure(figsize=(10, 6))
    ville_counts.plot(kind='bar')
    plt.title('Distribution des lieux de provenance des papyrus')
    plt.xlabel('Ville')
    plt.ylabel('Nombre de papyrus')
    plt.xticks(rotation=45)
    plt.show()


def nettoyer_dates(df):
    # Fonction pour nettoyer et formater les dates
    def formater_date(date_str):
        # Regex pour extraire les dates au format "AD xxx" ou "AD xxx - xxx"
        match = re.search(r'(AD\s*\d{1,4}(?:\s*-\s*AD\s*\d{1,4})?)', date_str)
        return match.group(0) if match else None

    # Appliquer la fonction de nettoyage sur la colonne Date
    df['Date'] = df['Date'].apply(formater_date)
    df = df.dropna(subset=['Date'])

    return df

def analyser_dates(df):
    # Compter la densité de papyrus par année
    df['Année'] = df['Date'].str.extract(r'AD\s*(\d{4})')[0]  # Extraire l'année
    df['Année'] = pd.to_numeric(df['Année'], errors='coerce')
    df = df.dropna(subset=['Année'])

    # Créer un histogramme pour représenter la densité de papyrus
    plt.figure(figsize=(12, 6))
    df['Année'].hist(bins=range(int(df['Année'].min()), int(df['Année'].max()) + 1), alpha=0.7)
    plt.title('Densité de papyrus par année')
    plt.xlabel('Année')
    plt.ylabel('Nombre de papyrus')
    plt.xticks(range(int(df['Année'].min()), int(df['Année'].max()) + 1, 10))  # Ajuste les ticks de l'axe x
    plt.show()






if __name__ == "__main__":
    # Configurer le parser d'arguments
    parser = argparse.ArgumentParser(description="Chargement, nettoyage et analyse du dataset de papyrus.")
    parser.add_argument('fichier_csv', help="Chemin du fichier CSV contenant les données de papyrus")
    args = parser.parse_args()

    # Charger et nettoyer le dataset
    dataset_nettoye = charger_et_nettoyer_dataset(args.fichier_csv)
    print("\nDataset après nettoyage et tri :")
    print(dataset_nettoye)

    # Analyse des genres
    analyser_genres(dataset_nettoye)

    # Analyse de la réutilisation
    analyser_reutilisation(dataset_nettoye)

    # Analyse des lieux
    analyser_villes(dataset_nettoye)

    # Nettoyage et analyse des dates
    dataset_nettoye = nettoyer_dates(dataset_nettoye)
    analyser_dates(dataset_nettoye)
