import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_comparateur_crises():
    st.title("⚖️ Comparateur de crises – Statistiques globales")

    # Charger les données
    try:
        df = pd.read_csv("tweet_clean.csv", parse_dates=["created_at"])
    except FileNotFoundError:
        st.error("Fichier tweet_clean.csv introuvable.")
        return

    # Vérification colonnes essentielles
    required_cols = {"tweet_id", "topic", "retweet_count", "favorite_count"}
    if not required_cols.issubset(df.columns):
        st.error("Colonnes manquantes dans le fichier.")
        return

    # Liste des topics
    topics = df["topic"].dropna().unique()
    selected = st.multiselect(
        "Sélectionne les crises à comparer",
        options=sorted(topics),
        default=sorted(topics)[:2]
    )

    if not selected:
        st.warning("Choisis au moins une crise.")
        return

    # Filtrage
    df_filtered = df[df["topic"].isin(selected)]

    # Calculs
    stats = df_filtered.groupby("topic").agg(
        Nombre_de_tweets=("tweet_id", "count"),
        Total_retweets=("retweet_count", "sum"),
        Moyenne_likes=("favorite_count", "mean")
    ).reset_index()

    stats["Moyenne_likes"] = stats["Moyenne_likes"].round(2)

    # 🔹 Tableau
    st.subheader("📋 Statistiques comparées")
    
    st.dataframe(stats, use_container_width=True)

    # 🔷 Barres groupées
    st.subheader("📊 Comparaison visuelle")
    stats_long = stats.melt(id_vars="topic", var_name="Indicateur", value_name="Valeur")
    fig_bar = px.bar(
        stats_long,
        x="topic",
        y="Valeur",
        color="Indicateur",
        barmode="group",
        text_auto=True,
        title="Comparaison des indicateurs par crise"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # 🔸 Camembert
    st.subheader("🥧 Répartition du volume de tweets")
    fig_pie = px.pie(
        stats,
        values="Nombre_de_tweets",
        names="topic",
        title="Part relative du volume de tweets",
        hole=0.4
    )
    fig_pie.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
