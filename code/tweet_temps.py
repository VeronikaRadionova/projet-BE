import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_tweet_temps(dataframes, labels):
    label_to_code = {v: k for k, v in labels.items()}
    
    st.title("📈 Évolution des tweets dans le temps")

    if "Tweet_date_clean" not in dataframes:
        st.error("Tweet_date_clean est manquant dans les données chargées.")
        return

    df = dataframes["Tweet_date_clean"]

    required_columns = {"topic", "date"}
    if not required_columns.issubset(df.columns):
        st.error("Colonnes attendues manquantes dans le fichier.")
        return

    crises = df["topic"].dropna().unique()
    crises_lisibles = [labels.get(code, code) for code in sorted(crises)]
    selected_label = st.selectbox("Choisissez une crise 📍", crises_lisibles)
    selected_crisis = label_to_code.get(selected_label, selected_label)

    df_crisis = df[df["topic"] == selected_crisis].copy()
    df_crisis['date'] = pd.to_datetime(df_crisis['date'])
    tweet_counts = df_crisis.groupby('date').size().reset_index(name='Nombre de tweets')

    fig = px.line(
        tweet_counts, x='date', y='Nombre de tweets',
        title=f"Nombre de tweets au fil du temps pour la crise : {selected_label}",
        labels={'date': 'Date', 'Nombre de tweets': 'Nombre de tweets'}
    )

    fig.update_layout(xaxis_title="Date", yaxis_title="Nombre de tweets", title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Données journalières")
    st.dataframe(tweet_counts, use_container_width=True)

def format_crisis(trecisid, labels):
    return f"{labels.get(trecisid, trecisid)} ({trecisid})"
