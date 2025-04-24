import streamlit as st
import pandas as pd
import plotly.express as px

labels = {
    "TRECIS-CTIT-H-001": "fireColorado2012",
    "TRECIS-CTIT-H-002": "costaRicaEarthquake2012",
    "TRECIS-CTIT-H-003": "floodColorado2013",
    "TRECIS-CTIT-H-004": "typhoonPablo2012",
    "TRECIS-CTIT-H-005": "laAirportShooting2013",
    "TRECIS-CTIT-H-006": "westTexasExplosion2013",
    "TRECIS-CTIT-H-007": "guatemalaEarthquake2012",
    "TRECIS-CTIT-H-008": "italyEarthquakes2012",
    "TRECIS-CTIT-H-009": "philipinnesFloods2012",
    "TRECIS-CTIT-H-010": "albertaFloods2013",
    "TRECIS-CTIT-H-011": "australiaBushfire2013",
    "TRECIS-CTIT-H-012": "bostonBombings2013",
    "TRECIS-CTIT-H-013": "manilaFloods2013",
    "TRECIS-CTIT-H-014": "queenslandFloods2013",
    "TRECIS-CTIT-H-015": "typhoonYolanda2013",
    "TRECIS-CTIT-H-016": "joplinTornado2011",
    "TRECIS-CTIT-H-017": "chileEarthquake2014",
    "TRECIS-CTIT-H-018": "typhoonHagupit2014",
    "TRECIS-CTIT-H-019": "nepalEarthquake2015",
    "TRECIS-CTIT-H-020": "flSchoolShooting2018",
    "TRECIS-CTIT-H-021": "parisAttacks2015",
    "TRECIS-CTIT-H-022": "floodChoco2019",
    "TRECIS-CTIT-H-023": "fireAndover2019",
    "TRECIS-CTIT-H-024": "earthquakeCalifornia2014",
    "TRECIS-CTIT-H-025": "earthquakeBohol2013",
    "TRECIS-CTIT-H-026": "hurricaneFlorence2018",
    "TRECIS-CTIT-H-027": "shootingDallas2017",
    "TRECIS-CTIT-H-028": "fireYMM2016",
    "TRECIS-CTIT-H-029": "albertaWildfires2019",
    "TRECIS-CTIT-H-030": "cycloneKenneth2019",
    "TRECIS-CTIT-H-031": "philippinesEarthquake2019",
    "TRECIS-CTIT-H-032": "coloradoStemShooting2019",
    "TRECIS-CTIT-H-033": "southAfricaFloods2019",
    "TRECIS-CTIT-H-034": "sandiegoSynagogueShooting2019"
}

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
    selected_crisis = st.selectbox("Choisissez une crise 📍", sorted(crises), format_func=format)

    # Filtrage des tweets pour la crise sélectionnée
    df_crisis = df[df["topic"] == selected_crisis].copy()

    # Conversion en datetime
    df_crisis['date'] = pd.to_datetime(df_crisis['date'])

    # Grouper par date et compter
    tweet_counts = df_crisis.groupby('date').size().reset_index(name='Nombre de tweets')

    # Affichage avec Plotly
    fig = px.line(tweet_counts, x='date', y='Nombre de tweets',
                  title=f"Nombre de tweets au fil du temps pour la crise : {format(selected_crisis)}",
                  labels={'date': 'Date', 'Nombre de tweets': 'Nombre de tweets'})

    fig.update_layout(xaxis_title="Date", yaxis_title="Nombre de tweets", title_x=0.5)

    st.plotly_chart(fig, use_container_width=True)

    # Affichage d'un tableau résumé
    st.subheader("📊 Données journalières")
    st.dataframe(tweet_counts, use_container_width=True)

def format(trecisid):
    """
    Formate le texte pour l'affichage dans le selectbox.
    """
    return f"{labels[trecisid]} ({trecisid})" if trecisid in labels else trecisid