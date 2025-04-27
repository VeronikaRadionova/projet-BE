import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_comparateur_crises(dataframes, labels):
    st.title("⚖️ Comparateur de crises – Statistiques globales")

    if "Tweet_clean" not in dataframes:
        st.error("Le fichier 'Tweet_clean.csv' est manquant.")
        return

    df = dataframes["Tweet_clean"]

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
