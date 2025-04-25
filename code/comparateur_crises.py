import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_comparateur_crises(dataframes, labels):
    st.title("⚖️ Comparateur de crises – Statistiques globales")

    # Vérification de la présence du fichier nécessaire
    if "tweet_clean" not in dataframes:
        st.error("Le fichier 'tweet_clean.csv' est manquant dans le dossier CSV.")
        return

    df = dataframes["tweet_clean"]

    # Vérification des colonnes essentielles
    required_cols = {"tweet_id", "topic", "retweet_count", "favorite_count"}
    if not required_cols.issubset(df.columns):
        st.error("Colonnes nécessaires manquantes dans le DataFrame.")
        return

    # Liste des topics avec noms lisibles
    topics = df["topic"].dropna().unique()
    readable_topics = {topic: labels.get(topic, topic) for topic in topics}

    # Affichage du sélecteur
    selected_labels = st.multiselect(
        "Sélectionne les crises à comparer",
        options=[readable_topics[t] for t in sorted(topics)],
        default=[readable_topics[t] for t in sorted(topics)[:2]]
    )

    # Conversion inverse des labels sélectionnés en codes
    label_to_code = {v: k for k, v in readable_topics.items()}
    selected_codes = [label_to_code[label] for label in selected_labels if label in label_to_code]

    if not selected_codes:
        st.warning("Choisis au moins une crise.")
        return

    # Filtrage
    df_filtered = df[df["topic"].isin(selected_codes)]

    # Calculs
    stats = df_filtered.groupby("topic").agg(
        Nombre_de_tweets=("tweet_id", "count"),
        Total_retweets=("retweet_count", "sum"),
        Moyenne_likes=("favorite_count", "mean")
    ).reset_index()

    stats["Moyenne_likes"] = stats["Moyenne_likes"].round(2)
    stats["topic"] = stats["topic"].map(readable_topics)  # Remplacer les codes par noms lisibles

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
