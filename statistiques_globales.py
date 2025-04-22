import streamlit as st
import pandas as pd


def afficher_statistiques_globales():
    st.title("📊 Statistiques globales")

    try:
        df = pd.read_csv("tweet_clean.csv", parse_dates=["created_at"])
    except FileNotFoundError:
        st.error("Fichier tweet_clean.csv introuvable.")
        return

    st.markdown("### Vue d’ensemble des données")

    total_tweets = len(df)
    date_min = df["created_at"].min().date()
    date_max = df["created_at"].max().date()
    nb_topics = df["topic"].nunique()
    total_retweets = int(df["retweet_count"].sum())
    total_likes = int(df["favorite_count"].sum())

    nb_annotated = df["annotation_annotated"].sum()
    nb_high_priority = df[df["annotation_postPriority"] == "High"].shape[0]
    nb_sensitive = df["possibly_sensitive"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("📌 Tweets au total", f"{total_tweets:n}")
    col2.metric("🗓️ Période couverte", f"{date_min} → {date_max}")
    col3.metric("🔥 Crises détectées", f"{nb_topics}")

    col4, col5, col6 = st.columns(3)
    col4.metric("🔁 Retweets totaux", f"{total_retweets:n}")
    col5.metric("❤️ Likes totaux", f"{total_likes:n}")
    col6.metric("🚨 Tweets sensibles", f"{int(nb_sensitive)}")

    st.markdown("### 📍 Annotations")
    st.write(f"- Tweets annotés : **{int(nb_annotated)}**")
    st.write(f"- Tweets de priorité haute : **{nb_high_priority}**")

    # Tweet le plus retweeté
    if "text" in df.columns:
        top_tweet = df.loc[df["retweet_count"].idxmax()]
        st.markdown("### 🌟 Tweet le plus populaire")
        st.code(top_tweet["text"], language="markdown")
        st.write(f"Retweets : {top_tweet['retweet_count']} | Likes : {top_tweet['favorite_count']}")
