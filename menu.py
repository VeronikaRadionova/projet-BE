import streamlit as st
import tweet_temps
import hashtags_top
import statistiques_globales
import comparateur_crises
import suivi_detaille_crises
import gravite

# Configuration de la page
st.set_page_config(
    page_title="Tableau de bord des Tweets",
    page_icon="📊",
    layout="wide"
)

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

# Titre dans la sidebar
st.sidebar.title("📚 Menu principal")

# Choix de la page
page = st.sidebar.radio("Navigation", [
    "Accueil",
    "Vue d’ensemble",
    "Évolution des tweets dans le temps",
    "Top hashtags",
    "Comparateur de crises",
    "Suivi de crises",
    "Gravité"
])

# Affichage des pages
if page == "Accueil":
    st.title("Bienvenue sur le Tableau de bord des Tweets 📈")
    st.markdown(
        """
        Ce tableau de bord interactif vous permet d’explorer et d’analyser des données issues de Twitter en contexte de crise.  
        
        Utilisez le menu à gauche pour :
        - Voir des statistiques globales sur les tweets
        - Visualiser l’évolution des tweets dans le temps
        - Découvrir les hashtags les plus utilisés
        - Comparer des crises entre elles
        - Suivre une crise en particulier
        - Gravité
        - (À venir) Analyser les utilisateurs, les catégories, la localisation, etc.
        """
    )

elif page == "Vue d’ensemble":
    statistiques_globales.afficher_statistiques_globales()

elif page == "Évolution des tweets dans le temps":
    tweet_temps.afficher_tweet_temps()

elif page == "Top hashtags":
    hashtags_top.afficher_hashtag_ids_top()

elif page == "Comparateur de crises":
    comparateur_crises.afficher_comparateur_crises()

elif page == "Suivi de crises":
    suivi_detaille_crises.afficher_suivi_detaille_crises()

elif page == "Gravité":
    gravite.afficher_gravite()


with st.expander("Informations sur le projet"):
    st.markdown("""
    Ce projet est une analyse de tweets pendant une crise, visant à comprendre comment les informations sont diffusées et reçues.
    Nous utilisons des techniques de traitement de données en temps réel pour observer les tendances et influencer les décisions de gestion de crise.
    """)
