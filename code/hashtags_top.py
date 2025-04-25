import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_hashtag_ids_top(dataframes, labels):
    st.title("🏷️ Hashtags les plus utilisés")

    # Vérifie la présence du fichier nécessaire
    if "Hashtag_clean" not in dataframes:
        st.error("Le fichier 'Hashtag_clean.csv' est manquant dans le dossier CSV.")
        return

    df = dataframes["Hashtag_clean"]

    # Vérification des colonnes nécessaires
    required_columns = {"hashtag_id", "occurences"}
    if not required_columns.issubset(df.columns):
        st.error("Colonnes attendues manquantes dans le DataFrame.")
        return

    # Nettoyage des hashtags
    df['hashtag_id'] = df['hashtag_id'].astype(str).str.lower().str.strip()

    # Agrégation des occurrences
    top_hashtag_ids = df.groupby('hashtag_id')['occurences'].sum().reset_index()
    top_hashtag_ids = top_hashtag_ids.sort_values(by='occurences', ascending=False)

    # Slider interactif
    top_n = st.slider("Nombre de hashtags à afficher", min_value=5, max_value=30, value=10)

    # Affichage du graphique
    fig = px.bar(
        top_hashtag_ids.head(top_n),
        x='occurences',
        y='hashtag_id',
        orientation='h',
        title=f"Top {top_n} des hashtags les plus utilisés",
        labels={'occurences': 'Nombre d’occurrences', 'hashtag_id': 'Hashtag'}
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)

    # 🔹 Tableau associé
    st.subheader("📋 Tableau des hashtags")
    st.dataframe(top_hashtag_ids.head(top_n), use_container_width=True)
