#TODO faire/demenager les fonctions qui font de l'affichage
import streamlit as st
import variables
import pandas as pd
import sentiment
import plotly.express as px

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

def comparateurCrises(dataframes):
    labels = variables.getTrecisCrises(dataframes)
    
    st.title("⚖️ Comparateur de crises – Statistiques globales")

    if "Tweet_sentiment_localisation" not in dataframes:
        st.error("Le fichier 'Tweet_sentiment_localisation.csv' est manquant.")
        return

    df = dataframes["Tweet_sentiment_localisation"]

    required_cols = {"tweet_id", "topic", "retweet_count", "favorite_count"}
    if not required_cols.issubset(df.columns):
        st.error("Colonnes nécessaires manquantes.")
        return

    # Liste des topics lisibles
    topics = df["topic"].dropna().unique()
    readable_topics = {topic: labels.get(topic, topic) for topic in topics}

    selected_labels = st.multiselect(
        "📌 Sélectionnez les crises à comparer",
        options=[readable_topics[t] for t in sorted(topics)],
        default=[readable_topics[t] for t in sorted(topics)[:2]]
    )

    label_to_code = {v: k for k, v in readable_topics.items()}
    selected_codes = [label_to_code[label] for label in selected_labels if label in label_to_code]

    if not selected_codes:
        st.warning("Veuillez choisir au moins une crise.")
        return

    df_filtered = df[df["topic"].isin(selected_codes)]

    stats = df_filtered.groupby("topic").agg(
        Nombre_de_tweets=("tweet_id", "count"),
        Total_retweets=("retweet_count", "sum"),
        Moyenne_likes=("favorite_count", "mean")
    ).reset_index()

    stats["Moyenne_likes"] = stats["Moyenne_likes"].round(2)
    stats["topic"] = stats["topic"].map(readable_topics)

    # --- 📋 Tableau Résumé ---
    st.subheader("📋 Statistiques comparées")
    st.dataframe(stats, use_container_width=True)

    # --- 📊 Barres groupées : Tweets + Retweets ---
    st.subheader("📈 Comparaison du nombre de tweets et de retweets")
    stats_bar = stats.melt(id_vars="topic", value_vars=["Nombre_de_tweets", "Total_retweets"],
                           var_name="Indicateur", value_name="Valeur")

    fig_bar = px.bar(
        stats_bar,
        x="topic",
        y="Valeur",
        color="Indicateur",
        barmode="group",
        text_auto=True,
        title="Comparaison entre Nombre de Tweets et Total de Retweets"
    )
    fig_bar.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- 💬 Barres Moyenne de Likes ---
    st.subheader("👍 Comparaison de la moyenne des likes par tweet")
    fig_likes = px.bar(
        stats,
        x="topic",
        y="Moyenne_likes",
        color_discrete_sequence=["#FF69B4"],  # rose stylé
        text_auto=True,
        title="Moyenne de likes par tweet pour chaque crise"
    )
    fig_likes.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig_likes, use_container_width=True)

    # --- 🥧 Camembert Répartition Tweets ---
    st.subheader("🥧 Répartition du volume de tweets")
    fig_pie = px.pie(
        stats,
        values="Nombre_de_tweets",
        names="topic",
        title="Part relative du nombre de tweets",
        hole=0.4
    )
    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- 📈 Répartition du sentiment par crise ---
    st.subheader("💬 Répartition du sentiment par crise")
    sentiment_counts = df_filtered.groupby(["topic", "sentiment"]).size().reset_index(name="count")
    sentiment_counts["topic"] = sentiment_counts["topic"].map(readable_topics)

    fig_sentiment = px.bar(
        sentiment_counts,
        x="sentiment",
        y="count",
        color="topic",
        barmode="group",
        text_auto=True,
        title="Répartition des sentiments par crise",
        labels={"sentiment": "Sentiment", "count": "Nombre de Tweets"}
    )
    fig_sentiment.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig_sentiment, use_container_width=True)
     # --- 🥧 Répartition des catégories de posts ---
    st.subheader("📚 Répartition des catégories de posts")

    # Assurer que 'post_category' est bien une liste et exploser
    df_filtered['post_category'] = df_filtered['post_category'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    df_exploded = df_filtered.explode('post_category')

    # Supprimer les valeurs nulles après explosion
    df_exploded = df_exploded.dropna(subset=['post_category'])

    category_counts = df_exploded.groupby(["topic", "post_category"]).size().reset_index(name="count")
    category_counts["topic"] = category_counts["topic"].map(readable_topics)

    fig_category = px.bar(
        category_counts,
        x="post_category",
        y="count",
        color="topic",
        barmode="group",
        text_auto=True,
        title="Comparaison des types de posts entre crises",
        labels={"post_category": "Catégorie de Post", "count": "Nombre de Tweets"}
    )
    fig_category.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig_category, use_container_width=True)