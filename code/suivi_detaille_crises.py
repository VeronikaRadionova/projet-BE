import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_suivi_detaille_crises():
    st.title("🔎 Suivi détaillé des crises")

    # Chargement des données
    try:
        df = pd.read_csv("../CSV/Tweet_sentiment_localisation.csv", parse_dates=["created_at"])
    except FileNotFoundError:
        st.error("Fichier Tweet_sentiment_localisation.csv introuvable.")
        return

    if "topic" not in df.columns or "lieu_extrait" not in df.columns:
        st.error("Colonnes 'topic' ou 'lieu_extrait' manquantes.")
        return

    # Conversion de la colonne sentiment en valeurs numériques
    sentiment_map = {
        "positive": 1,
        "neutral": 0,
        "negative": -1
    }
    df["sentiment_numeric"] = df["sentiment"].map(sentiment_map)

    # Choix de localisation
    lieux = df["lieu_extrait"].dropna().unique()
    lieu_selectionne = st.selectbox("📍 Filtrer par lieu :", options=sorted(lieux))

    # Filtrage par lieu
    df_lieu = df[df["lieu_extrait"] == lieu_selectionne]

    # Liste des événements (topics) actifs à cet endroit
    st.subheader("📋 Événements actifs")
    tri = st.selectbox("Trier par :", options=["Gravité", "Nombre de tweets", "Date"])
    group = df_lieu.groupby("topic").agg(
        nb_tweets=("tweet_id", "count"),
        total_retweets=("retweet_count", "sum"),
        date_plus_recent=("created_at", "max"),
        sentiment_moyen=("sentiment_numeric", "mean")
    ).reset_index()

    if tri == "Gravité":
        group = group.sort_values("total_retweets", ascending=False)
    elif tri == "Nombre de tweets":
        group = group.sort_values("nb_tweets", ascending=False)
    else:
        group = group.sort_values("date_plus_recent", ascending=False)

    st.dataframe(group, use_container_width=True)

    # Sélection d'un événement à détailler
    selected_topic = st.selectbox("🧵 Sélectionner un événement :", group["topic"])

    df_event = df_lieu[df_lieu["topic"] == selected_topic]

    st.subheader(f"🧾 Détails de l'événement : {selected_topic}")
    st.markdown(f"- **Lieu** : {lieu_selectionne}")
    st.markdown(f"- **Nombre de tweets** : {len(df_event)}")
    st.markdown(f"- **Sentiment moyen** : {df_event['sentiment_numeric'].mean():.2f}")
    st.markdown(f"- **Dernier tweet** : {df_event['created_at'].max().strftime('%Y-%m-%d %H:%M')}")

    st.subheader("📝 Tweets associés")
    for _, row in df_event.sort_values("created_at", ascending=False).head(10).iterrows():
        st.markdown(f"📅 *{row['created_at']}* – ❤️ {row['favorite_count']} – 🔁 {row['retweet_count']}")
        st.markdown(f"> {row['text']}")
        st.markdown("---")

    # Fréquence dans le temps
    st.subheader("📈 Fréquence des tweets")
    df_event["date"] = df_event["created_at"].dt.date
    freq = df_event.groupby("date").size().reset_index(name="nb_tweets")
    fig_freq = px.line(freq, x="date", y="nb_tweets", markers=True, title="Évolution du volume de tweets")
    st.plotly_chart(fig_freq, use_container_width=True)

    # Sentiment dans le temps
    st.subheader("📊 Sentiment au fil du temps")
    sent = df_event.groupby("date")["sentiment_numeric"].mean().reset_index()
    fig_sent = px.line(sent, x="date", y="sentiment_numeric", markers=True, title="Évolution du sentiment")
    st.plotly_chart(fig_sent, use_container_width=True)
