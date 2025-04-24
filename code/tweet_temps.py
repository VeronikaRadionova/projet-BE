import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_tweet_temps():
    st.title("📈 Évolution des tweets dans le temps")
    
    try:
        df = pd.read_csv("../CSV/Tweet_date_clean.csv")
    except FileNotFoundError:
        st.error("Fichier Tweet_date_clean.csv introuvable.")
        return

    # Vérification des colonnes nécessaires
    required_columns = {"topic", "date"}
    if not required_columns.issubset(df.columns):
        st.error("Colonnes attendues manquantes dans le fichier.")
        return

    # Liste des crises disponibles
    crises = df["topic"].dropna().unique()
    selected_crisis = st.selectbox("Choisissez une crise 📍", sorted(crises))

    # Filtrage des tweets pour la crise sélectionnée
    df_crisis = df[df["topic"] == selected_crisis].copy()

    # Conversion en datetime
    df_crisis['date'] = pd.to_datetime(df_crisis['date'])

    # Grouper par date et compter
    tweet_counts = df_crisis.groupby('date').size().reset_index(name='Nombre de tweets')

    # Affichage avec Plotly
    fig = px.line(tweet_counts, x='date', y='Nombre de tweets',
                  title=f"Nombre de tweets au fil du temps pour la crise : {selected_crisis}",
                  labels={'date': 'Date', 'Nombre de tweets': 'Nombre de tweets'})

    fig.update_layout(xaxis_title="Date", yaxis_title="Nombre de tweets", title_x=0.5)

    st.plotly_chart(fig, use_container_width=True)

    # Affichage d'un tableau résumé
    st.subheader("📊 Données journalières")
    st.dataframe(tweet_counts, use_container_width=True)

