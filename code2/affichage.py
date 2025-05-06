#TODO faire/demenager les fonctions qui font de l'affichage
import streamlit as st
import variables
import pandas as pd
import sentiment

def accueil():
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
def vueEnsemble():
    return 0

def suiviCrise(data):
    st.title("🔎 Analyse et suivi d'une crise : Volume & Sentiments")

    selected_label=st.selectbox("Crises",variables.getCrises(data))
    st.markdown(f"- **Crise sélectionnée** : {selected_label}")
    df= data["Tweet_sentiment_localisation"]
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df_crisis= df[(df["topic"]==variables.getCrisesTrecis(data)[selected_label])]
    st.markdown(f"- **Nombre de tweets** : {len(df_crisis)}")
    dernier_tweet = df_crisis["created_at"].max()
    if pd.notnull(dernier_tweet):
        st.markdown(f"- **Dernier tweet** : {dernier_tweet.strftime('%Y-%m-%d %H:%M')}")

    sentiment.repartitionSentiment(df_crisis)
    sentiment.sentimentMoyen(df_crisis)


def recherchePersonnalise():
    return 0