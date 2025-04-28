import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Tableau de bord des Tweets",
    page_icon="📊",
    layout="wide"
)

import hashtags_top
import statistiques_globales
import comparateur_crises
import carte_globale
import gravite
import demande_aide_final
import top_influenceur
import recherche_personnalisee
import analyse_et_comparaison_crises
import base64
import os
import pandas as pd
import statsGlobV2
import analyse_et_comparaison_crisesV2

# Injection de CSS personnalisé via st.markdown
st.markdown("""
    <style>
        /* Changer le fond de la page */
        body {
            background-color: #f4f4f9;
            font-family: 'Arial', sans-serif;
        }

        /* Personnaliser le titre */
        .css-18e3th9 {
            color: #5e4b7b;
            font-size: 3em;
            font-weight: bold;
        }

        /* Personnaliser les boutons et sliders */
        .css-1d391kg {
            background-color: #5e4b8b;
            color: white;
            border-radius: 8px;
            padding: 10px;
        }

        .css-1d391kg:hover {
            background-color: #7a5abf;
        }

        /* Personnaliser les headers */
        h1 {
            color: #5e4b8b;
        }

        h2, h3 {
            color: #4b3e70;
        }

        /* Personnaliser les tableaux */
        .streamlit-expanderHeader {
            font-size: 1.2em;
            color: #4b3e70;
        }

        .css-12oz5g7 {
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        html, body, .stApp {{
            height: 100%;
            margin: 0;
            padding: 0;
        }}

        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: 100% 100%;   /* force largeur ET hauteur */
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center center;
            background-color: rgba(255, 255, 255, 0.2); /* Couleur de fond blanche avec 50% de transparence */
            background-blend-mode: lighten; /* Mélange l'image avec la couleur de fond */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# """
# Importation du data dans le repertoire CSV
csv_path = "../CSV"
dataframes = {}

for file_name in os.listdir(csv_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(csv_path, file_name)
        df_name = os.path.splitext(file_name)[0]
        dataframes[df_name] = pd.read_csv(file_path, low_memory=False)

labels = {
    "TRECIS-CTIT-H-001": "fireColorado2012",
    "TRECIS-CTIT-H-002": "costaRicaEarthquake2012",
    "TRECIS-CTIT-H-003": "floodColorado2013",
    "TRECIS-CTIT-H-004": "typhoonPablo2012",
    "TRECIS-CTIT-H-005": "laAirportShooting2013",
    "TRECIS-CTIT-H-006": "westTexasExplosion2013",
    "TRECIS-CTIT-H-007": "guatemalaEarthquake2012",
    "TRECIS-CTIT-H-008": "italyEarthquakes2012",
    "TRECIS-CTIT-H-009": "philipinnesFloods2012",
    "TRECIS-CTIT-H-010": "albertaFloods2013",
    "TRECIS-CTIT-H-011": "australiaBushfire2013",
    "TRECIS-CTIT-H-012": "bostonBombings2013",
    "TRECIS-CTIT-H-013": "manilaFloods2013",
    "TRECIS-CTIT-H-014": "queenslandFloods2013",
    "TRECIS-CTIT-H-015": "typhoonYolanda2013",
    "TRECIS-CTIT-H-016": "joplinTornado2011",
    "TRECIS-CTIT-H-017": "chileEarthquake2014",
    "TRECIS-CTIT-H-018": "typhoonHagupit2014",
    "TRECIS-CTIT-H-019": "nepalEarthquake2015",
    "TRECIS-CTIT-H-020": "flSchoolShooting2018",
    "TRECIS-CTIT-H-021": "parisAttacks2015",
    "TRECIS-CTIT-H-022": "floodChoco2019",
    "TRECIS-CTIT-H-023": "fireAndover2019",
    "TRECIS-CTIT-H-024": "earthquakeCalifornia2014",
    "TRECIS-CTIT-H-025": "earthquakeBohol2013",
    "TRECIS-CTIT-H-026": "hurricaneFlorence2018",
    "TRECIS-CTIT-H-027": "shootingDallas2017",
    "TRECIS-CTIT-H-028": "fireYMM2016",
    "TRECIS-CTIT-H-029": "albertaWildfires2019",
    "TRECIS-CTIT-H-030": "cycloneKenneth2019",
    "TRECIS-CTIT-H-031": "philippinesEarthquake2019",
    "TRECIS-CTIT-H-032": "coloradoStemShooting2019",
    "TRECIS-CTIT-H-033": "southAfricaFloods2019",
    "TRECIS-CTIT-H-034": "sandiegoSynagogueShooting2019"
}

label_to_code = {v: k for k, v in labels.items()}

# Titre dans la sidebar
st.sidebar.title("📚 Menu principal")

choixVersion=st.sidebar.radio("Choix version",["V1","V2"])

if choixVersion== "V1":
    # Choix de la page
    page = st.sidebar.radio("Navigation", [
        "Accueil",
        "Vue d’ensemble",
        "Analyse et suivi d'une crise",
        "Recherche personnalisée",
        "Top hashtags",
        "Comparateur de crises",
        "Carte globale des tweets",
        "Gravité",
        "Demande d'aide",
        "Top influenceur"
    ])

    # Affichage des pages
    if page == "Accueil":
        st.title("Bienvenue sur le Tableau de bord des Tweets 📈")
        st.markdown(
            """
            Ce tableau de bord interactif vous permet d’explorer et d’analyser des données issues de Twitter en contexte de crise.  
            
            Utilisez le menu à gauche pour :
            - Voir des statistiques globales sur les tweets
            - Faire des recherches personnalisees
            - Découvrir les hashtags les plus utilisés
            - Comparer des crises entre elles
            - Suivre une crise en particulier
            - Gravité
            - Demande d'aide
            - Top influenceur
            - (À venir) Analyser les utilisateurs, les catégories, la localisation, etc.
            """
        )

    elif page == "Vue d’ensemble":
        statistiques_globales.afficher_statistiques_globales(dataframes,labels)

    elif page == "Recherche personnalisée":
        recherche_personnalisee.recherche_personnalisee(dataframes,labels)

    elif page == "Top hashtags":
        hashtags_top.afficher_hashtag_ids_top(dataframes,labels)

    elif page == "Comparateur de crises":
        comparateur_crises.afficher_comparateur_crises(dataframes,labels)

    elif page == "Carte globale des tweets":
        carte_globale.afficher_carte_globale(dataframes,labels)

    elif page == "Gravité":
        gravite.afficher_gravite(dataframes,labels)

    elif page == "Demande d'aide":
        demande_aide_final.demande_aide(dataframes,labels)

    elif page == "Top influenceur":
        top_influenceur.top_influenceurs(dataframes,labels)

    elif page == "Analyse et suivi d'une crise":
        analyse_et_comparaison_crises.analyse_complete_crise(dataframes, labels)

    with st.expander("Informations sur le projet"):
        st.markdown("""
        Ce projet est une analyse de tweets pendant une crise, visant à comprendre comment les informations sont diffusées et reçues.
        Nous utilisons des techniques de traitement de données en temps réel pour observer les tendances et influencer les décisions de gestion de crise.
        """)
elif choixVersion=="V2":
    page = st.sidebar.radio("Navigation", [
        "Accueil",
        "Vue d’ensemble",
        "Suivi de crise",
        "Comparateur de crises",
        "Demande d'aide",
        "Recherche personnalisée"
    ])

    # Affichage des pages
    if page == "Accueil":
        st.title("Bienvenue sur le Tableau de bord des Tweets 📈")
        st.markdown(
            """
            Ce tableau de bord interactif vous permet d’explorer et d’analyser des données issues de Twitter en contexte de crise.  
            
            Utilisez le menu à gauche pour :
            - Voir des statistiques globales sur les tweets
            - Faire des recherches personnalisees
            - Visualiser l’évolution des tweets dans le temps
            - Découvrir les hashtags les plus utilisés
            - Comparer des crises entre elles
            - Suivre une crise en particulier
            - Gravité
            - Demande d'aide
            - Top influenceur
            - (À venir) Analyser les utilisateurs, les catégories, la localisation, etc.
            """
        )
    elif page == "Vue d’ensemble":
        statsGlobV2.afficher_statistiques_globales(dataframes,labels) 
      
    elif page == "Recherche personnalisée":
        recherche_personnalisee.recherche_personnalisee(dataframes,labels)
    elif page == "Suivi de crise":
        analyse_et_comparaison_crisesV2.analyse_complete_crise(dataframes, labels)
    elif page == "Demande d'aide":
        demande_aide_final.demande_aide(dataframes,labels)
    elif page == "Comparateur de crises":
        comparateur_crises.afficher_comparateur_crises(dataframes,labels)