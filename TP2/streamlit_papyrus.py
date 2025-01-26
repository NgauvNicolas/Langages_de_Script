import streamlit as st
import pandas as pd
import re

# Titre de l'application
st.title("La Chasse aux Papyrus")
# Image d'illustration
st.image("https://upload.wikimedia.org/wikipedia/commons/2/28/000_P.Lit.Lond._96_col._i.jpg",
         caption="Exploration des Papyrus de l'époque hellénistique", use_container_width=True)
# Description
st.write(
    """
    Bienvenue dans l'application **La Chasse aux Papyrus** !
    Cette application vous permet d'explorer une collection fascinante de papyry grecs.
    Découvrez les informations principales sur chaque papyrus, filtrez-les par provenance et date, cherchez-les par mot-clé, et examinez les irrégularités textuelles des scribes antiques.
    """
)

st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choisissez une page", ["Explorer les papyrus", "Statistiques des irrégularités textuelles"])

# Chargement des données
# Glisser le fichier CSV qui nous intéresse : ici, "clean_papyrus-corpus.csv"
# On aurait pu le charger directement avec df = pd.read_csv('clean_papyrus-corpus.csv') mais quand on laisse l'utilisateur charger lui-même le fichier, l'application est plus ergonomique et modulaire !
uploaded_file = st.file_uploader("Chargez votre fichier CSV, par exemple : 'clean_papyrus-corpus.csv'", type="csv")
if uploaded_file:
    # Lecture des données
    data = pd.read_csv(uploaded_file)

    # Nettoyage et extraction des informations nécessaires
    data['parsed_date'] = data['Date'].str.extract(r'(\d{3,4})').astype(float)  # Extraction de l'année

    if page == "Explorer les papyrus":
        # Filtrage par lieu et date
        st.sidebar.header("Filtres")
        provenance_list = sorted(data['Provenance'].dropna().unique())
        selected_provenance = st.sidebar.selectbox("Provenance", ["Tous"] + provenance_list, index=0)
        min_date, max_date = int(data['parsed_date'].min()), int(data['parsed_date'].max())
        selected_date_range = st.sidebar.slider("Plage de dates", min_date, max_date, (min_date, max_date))

        filtered_data = data.copy()
        if selected_provenance != "Tous":
            filtered_data = filtered_data[filtered_data['Provenance'] == selected_provenance]
        filtered_data = filtered_data[
            (filtered_data['parsed_date'] >= selected_date_range[0]) &
            (filtered_data['parsed_date'] <= selected_date_range[1])
        ]

        # Sélection d'un papyrus
        papyrus_list = filtered_data['ID'].tolist()
        selected_papyrus = st.sidebar.selectbox("Choisissez un papyrus", options=papyrus_list)

        if selected_papyrus:
            st.subheader(f"Papyrus {selected_papyrus}")
            papyrus_data = filtered_data[filtered_data['ID'] == selected_papyrus].iloc[0]

            # Informations principales
            st.write("### Informations principales")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Date**")
                st.write(papyrus_data['Date'])
                st.write("**Provenance**")
                st.write(papyrus_data['Provenance'])
            with col2:
                st.write("**Personnes mentionnées**")
                people = eval(papyrus_data['People List']) if pd.notna(papyrus_data['People List']) else []
                for idx, person in enumerate(people):
                    if st.button(person, key=f"person_{idx}_{selected_papyrus}"):
                        related_papyri = data[data['People List'].str.contains(person, na=False)]['ID'].tolist()
                        st.write(f"Papyri mentionnant {person}: {', '.join(map(str, related_papyri))}")
                st.write("**Lieux mentionnés**")
                places = eval(papyrus_data['Places List']) if pd.notna(papyrus_data['Places List']) else []
                for idx, place in enumerate(places):
                    if st.button(place, key=f"place_{idx}_{selected_papyrus}"):
                        related_papyri = data[data['Places List'].str.contains(place, na=False)]['ID'].tolist()
                        st.write(f"Papyri mentionnant {place}: {', '.join(map(str, related_papyri))}")

            # Affichage des irrégularités textuelles sous forme clé/valeur
            st.write("### Textual Irregularities")
            irregularities = papyrus_data['Text Irregularities']
            if pd.isna(irregularities) or irregularities == "[]":
                st.write("Aucune irrégularité textuelle relevée.")
            else:
                st.write(irregularities)

            # Contenu des papyry
            st.write("### Contenu complet des papyry avec correction des irrégularités textuelles intégrée directement au texte")
            full_text = papyrus_data['Full Text']
            irregularities = eval(papyrus_data['Text Irregularities']) if pd.notna(papyrus_data['Text Irregularities']) else []
            annotated_text = full_text
            for irregularity in irregularities:
                try:
                    original, correction = irregularity.split(": read ")
                    annotated_text = re.sub(
                        rf"\b{original.strip()}\b",
                        f"~~{original.strip()}~~ **{correction.strip()}**",
                        annotated_text
                    )
                except ValueError:
                    continue
            st.markdown(annotated_text)

        # Ajout d'une fonctionnalité supplémentaire à l'application : une section de recherche
        st.sidebar.markdown("## Recherche par mot-clé")
        search_query = st.sidebar.text_input("Entrez un mot ou une phrase à rechercher :", "")

        if search_query:
            # Filtrer les papyri contenant le mot-clé dans 'Full Text'
            filtered_papyri = data[data['Full Text'].str.contains(search_query, case=False, na=False)]

            st.markdown(f"### Résultats pour la recherche : '{search_query}'")
            if not filtered_papyri.empty:
                for _, papyrus in filtered_papyri.iterrows():
                    st.markdown(f"**Papyrus ID : {papyrus['ID']}**")
                    st.write(f"**Date :** {papyrus['Date']}")
                    st.write(f"**Provenance :** {papyrus['Provenance']}")

                    # Extrait du texte avec le mot-clé mis en surbrillance
                    full_text = papyrus['Full Text']
                    highlighted_text = re.sub(
                        f"({re.escape(search_query)})",
                        r"**\1**",
                        full_text,
                        flags=re.IGNORECASE
                    )
                    st.markdown(f"**Extrait :** {highlighted_text[:500]}...")  # Limiter l'affichage pour les textes longs

                    st.markdown("---")
            else:
                st.write("Aucun résultat trouvé.")

    elif page == "Statistiques des irrégularités textuelles":
        st.subheader("Statistiques des irrégularités textuelles")
        data['irregularity_count'] = data['Text Irregularities'].apply(
            lambda x: len(eval(x)) if pd.notna(x) else 0
        )

        st.write("### Nombre d'irrégularités par papyrus")
        st.bar_chart(data.set_index('ID')['irregularity_count'])

        st.write("### Fréquences des corrections")
        corrections = []
        for row in data['Text Irregularities'].dropna():
            corrections.extend(eval(row))
        correction_types = pd.Series(corrections).value_counts()
        st.bar_chart(correction_types)
