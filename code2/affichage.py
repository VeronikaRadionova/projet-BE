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
    #TODO rajouter la gravite
    #TODO rajouter la demande d'aide


def recherchePersonalisee(dataframes):

    labels = variables.getTrecisCrises(dataframes)

    st.title("🔎 Recherche personnalisée dans les tweets")

    if "Tweet_sentiment_localisation" not in dataframes:
        st.error("Le fichier 'Tweet_sentiment_localisation.csv' est manquant.")
        return

    df = dataframes["Tweet_sentiment_localisation"].copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["topic"] = df["topic"].map(labels).fillna(df["topic"])

    st.markdown("Filtre les tweets selon tes propres critères 👇")

    # 🔤 Filtrage par mot-clé
    keyword = st.text_input("🔤 Contient le mot-clé :")
    if keyword:
        df = df[df["text"].str.contains(keyword, case=False, na=False)]

    # 📅 Filtrage par date
    min_date = df["created_at"].min().date()
    max_date = df["created_at"].max().date()
    date_range = st.slider("📅 Plage de dates :", min_value=min_date, max_value=max_date,
                           value=(min_date, max_date))
    df = df[(df["created_at"].dt.date >= date_range[0]) & (df["created_at"].dt.date <= date_range[1])]

    # 📍 Filtrage par lieu
    lieux = df["lieu_extrait"].dropna().unique()
    lieux_selectionnes = st.multiselect("📍 Lieu :", options=sorted(lieux))
    if lieux_selectionnes:
        df = df[df["lieu_extrait"].isin(lieux_selectionnes)]

    # 🎭 Filtrage par sentiment
    sentiments =["Tous","Positif","Neutre","Negatif"]
    sentMap={"Positif":"positive","Negatif":"negative","Neutre":"neutral"}
    
    #sentiments_selectionnes = st.multiselect("🎭 Sentiment :", options=sorted(sentiments))
    sentiments_selectionnes= st.pills("🎭 Sentiment :",options=sentiments,selection_mode="single",default="Tous")
    if sentiments_selectionnes!="Tous":
        df = df[df["sentiment"].isin([sentMap[sentiments_selectionnes]])]

    # 📄 Affichage des résultats
    st.markdown(f"📄 **{len(df)} tweets** trouvés avec ces filtres.")
    st.dataframe(
        df[["created_at", "text", "sentiment", "lieu_extrait", "topic"]]
        .sort_values("created_at", ascending=False),
        use_container_width=True
    )

    # ⬇️ Export CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Télécharger les résultats", data=csv, file_name="tweets_filtrés.csv", mime="text/csv")
