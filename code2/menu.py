import streamlit as st

import affichage
import base64
import variables
# Configuration de la page
st.set_page_config(
    page_title="Tableau de bord des Tweets",
    page_icon="📊",
    layout="wide"
)


import os
import pandas as pd

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
    affichage.accueil()
elif page == "Vue d’ensemble":
    affichage.afficher_statistiques_globales(dataframes,labels) 
elif page == "Recherche personnalisée":
    affichage.recherche_personnalisee(dataframes,labels)
elif page == "Suivi de crise":
    affichage.suiviCrise(dataframes)
elif page == "Demande d'aide":
    affichage.demande_aide(dataframes,labels)
elif page == "Comparateur de crises":
    affichage.afficher_comparateur_crises(dataframes,labels)