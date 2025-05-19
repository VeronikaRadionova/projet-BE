import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# ------------------------- AFFICHAGE GRAVITÉ -------------------------

def afficher_gravite_plotly(df, titre_suffixe=""):
    colonne_gravite = 'annotation_postPriority'
    if colonne_gravite in df.columns:
        gravite_counts = df[colonne_gravite].value_counts()

        st.subheader(f'Répartition des gravités {titre_suffixe}')
        st.write(gravite_counts)

        graph_type = st.radio("Choisissez le type de graphique", ["Barres", "Camembert"], key=f"radio_graph_{titre_suffixe}")

        if graph_type == "Barres":
            fig = px.bar(
                gravite_counts,
                x=gravite_counts.index,
                y=gravite_counts.values,
                labels={'x': 'Gravité', 'y': 'Nombre de tweets'},
                title=f'Répartition des niveaux de gravité {titre_suffixe}',
                color=gravite_counts.index,
                color_discrete_map={
                    'Low': 'green',
                    'Medium': 'orange',
                    'High': 'red',
                    'Unknown': 'gray',
                    'Critical': 'black'
                }
            )
        else:
            fig = px.pie(
                names=gravite_counts.index,
                values=gravite_counts.values,
                title=f'Répartition des niveaux de gravité {titre_suffixe}',
                color=gravite_counts.index,
                color_discrete_map={
                    'Low': 'green',
                    'Medium': 'orange',
                    'High': 'red',
                    'Unknown': 'gray',
                    'Critical': 'black'
                }
            )

        st.plotly_chart(fig)
    else:
        st.error(f"La colonne '{colonne_gravite}' n'existe pas dans ce fichier.")

# ------------------------- GRAVITÉ PAR ÉVÉNEMENT -------------------------

def afficher_gravite_event_plotly(df, titre_suffixe=""):
    colonne_gravite = 'annotation_postPriority'
    colonne_eventid = 'crise_id'
    colonne_trecis_id = 'topic'

    if colonne_gravite in df.columns and colonne_eventid in df.columns and colonne_trecis_id in df.columns:
        df[colonne_eventid] = df[colonne_eventid].astype(str)
        eventids = sorted(df[colonne_eventid].unique())
        selected_eventid = st.selectbox('Sélectionne un Event ID', eventids)

        df_event = df[df[colonne_eventid] == selected_eventid]

        if not df_event.empty:
            trecis_id = df_event[colonne_trecis_id].iloc[0]
            st.write(f"TRECIS ID associé à {selected_eventid} : {trecis_id}")

            gravite_counts = df_event[colonne_gravite].value_counts().reindex(
                ['Low', 'Medium', 'High', 'Unknown', 'Critical'], fill_value=0
            )

            st.subheader(f'Répartition des gravités pour {selected_eventid} ({trecis_id}) {titre_suffixe}')
            st.write(gravite_counts)

            graph_type = st.radio("Choisissez le type de graphique", ["Barres", "Camembert"], key=f"radio_graph_event_{selected_eventid}")

            if graph_type == "Barres":
                fig = px.bar(
                    gravite_counts,
                    x=gravite_counts.index,
                    y=gravite_counts.values,
                    labels={'x': 'Gravité', 'y': 'Nombre de tweets'},
                    title=f'Répartition des niveaux de gravité pour {selected_eventid} ({trecis_id})',
                    color=gravite_counts.index,
                    color_discrete_map={
                        'Low': 'green',
                        'Medium': 'orange',
                        'High': 'red',
                        'Unknown': 'gray',
                        'Critical': 'black'
                    }
                )
            else:
                fig = px.pie(
                    names=gravite_counts.index,
                    values=gravite_counts.values,
                    title=f'Répartition des niveaux de gravité pour {selected_eventid} ({trecis_id})',
                    color=gravite_counts.index,
                    color_discrete_map={
                        'Low': 'green',
                        'Medium': 'orange',
                        'High': 'red',
                        'Unknown': 'gray',
                        'Critical': 'black'
                    }
                )

            st.plotly_chart(fig)
        else:
            st.warning(f"Aucune donnée trouvée pour Event ID : {selected_eventid}")
    else:
        st.error(f"Les colonnes '{colonne_gravite}', '{colonne_eventid}' ou '{colonne_trecis_id}' sont manquantes.")

# ------------------------- WORDCLOUD POUR GRAVITÉ ÉLEVÉE -------------------------

def afficher_wordcloud_gravite(df, gravites_filtrees=["High", "Critical"]):
    colonne_gravite = 'annotation_postPriority'
    colonne_texte = 'text'  # À adapter si ton texte est ailleurs

    if colonne_gravite in df.columns and colonne_texte in df.columns:
        df_filtre = df[df[colonne_gravite].isin(gravites_filtrees)]
        
        if df_filtre.empty:
            st.warning("Aucun tweet avec gravité élevée trouvé.")
            return
        
        texte_complet = " ".join(str(t) for t in df_filtre[colonne_texte])

        stopwords = set(STOPWORDS)
        stopwords.update(["https", "co", "RT", "amp"])  # Twitter-specific

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            stopwords=stopwords,
            colormap='Reds',
            max_words=100
        ).generate(texte_complet)

        st.subheader("🧠 Nuage de mots pour les tweets à gravité élevée")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.error(f"Les colonnes '{colonne_gravite}' ou '{colonne_texte}' sont manquantes.")

#------------------------- GRAVITE PAR CATEGORIE -------------------------

def afficher_gravite_par_categorie(df, titre_suffixe=""):
    colonne_gravite = 'annotation_postPriority'
    colonne_categorie = 'category_label'

    if colonne_gravite in df.columns and colonne_categorie in df.columns:
        categories = sorted(df[colonne_categorie].dropna().unique())
        selected_category = st.selectbox("Sélectionne une catégorie", categories)

        df_filtre = df[df[colonne_categorie] == selected_category]
        gravite_counts = df_filtre[colonne_gravite].value_counts().reindex(
            ['Low', 'Medium', 'High', 'Unknown', 'Critical'], fill_value=0
        )

        st.subheader(f"Gravité pour la catégorie : {selected_category} {titre_suffixe}")
        st.write(gravite_counts)

        graph_type = st.radio("Type de graphique", ["Barres", "Camembert"], key=f"radio_cat_{selected_category}")

        if graph_type == "Barres":
            fig = px.bar(
                gravite_counts,
                x=gravite_counts.index,
                y=gravite_counts.values,
                labels={'x': 'Gravité', 'y': 'Nombre de tweets'},
                title=f'Répartition des niveaux de gravité pour la catégorie "{selected_category}"',
                color=gravite_counts.index,
                color_discrete_map={
                    'Low': 'green',
                    'Medium': 'orange',
                    'High': 'red',
                    'Unknown': 'gray',
                    'Critical': 'black'
                }
            )
        else:
            fig = px.pie(
                names=gravite_counts.index,
                values=gravite_counts.values,
                title=f'Gravité pour la catégorie "{selected_category}"',
                color=gravite_counts.index,
                color_discrete_map={
                    'Low': 'green',
                    'Medium': 'orange',
                    'High': 'red',
                    'Unknown': 'gray',
                    'Critical': 'black'
                }
            )

        st.plotly_chart(fig)
    else:
        st.error("Les colonnes 'category_label' ou 'annotation_postPriority' sont absentes dans les données.")

gravite_couleurs = {
    "Low": "#d4edda",
    "Medium": "#fff3cd",
    "High": "#FF7F32",
    "Critical": "#f5c6cb",
    "Unknown": "#f0f0f0"
}

def afficher_tweets_gravite(df):
    with st.expander("📃 Aperçu de quelques tweets classés par gravité"):
        gravite_niveaux = ["Low", "Medium", "High", "Critical"]
        colonnes_affichables = [g for g in gravite_niveaux if not df[df["annotation_postPriority"] == g].empty]
        colonnes = st.columns(len(colonnes_affichables))
        for i, gravite in enumerate(colonnes_affichables):
            with colonnes[i]:
                st.markdown(f"### {gravite}")
                subset = df[df["annotation_postPriority"] == gravite].head(5)
                for _, row in subset.iterrows():
                    texte = row.get("text", "")
                    couleur = gravite_couleurs.get(gravite, "#f0f0f0")
                    st.markdown(
                        f"""
                        <div style="background-color:{couleur}; padding: 10px; border-radius: 10px; margin-bottom:10px; border: 1px solid #ccc;">
                            <p style="margin: 0; font-size: 14px;">{texte}</p>
                        </div>""",
                        unsafe_allow_html=True
                    )


# ------------------------- AFFICHAGE GENERAL DE LA PAGE -------------------------
def afficher_gravite(dataframes, labels) : 

    st.title('📊 Visualisation du Degré de Gravité des Tweets')

    dfs = {
        "Tous les Tweets": dataframes["Tweet_clean"],
        "Wildfire": dataframes["tweets_wildfire"],
        "Bombing": dataframes["tweets_bombing"],
        "Flood": dataframes["tweets_flood"],
        "Earthquake": dataframes["tweets_earthquake"],
        "Shooting": dataframes["tweets_shooting"],
        "Typhoon": dataframes["tweets_typhoon"],
    }

    df_categories = dataframes["tweets_par_categorie"]
    df_event = dataframes["tweets_par_event"]

    tab1, tab2, tab3, tab4 = st.tabs([
        " Gravité par type d'événement",
        " Gravité par Crise",
        " Gravité par Catégorie",
        " Nuage de mots (gravité élevée)"
    ])

    with tab1:
        st.header("Gravité selon le type d'événement")
        evenement = st.selectbox("Sélectionnez un type d'événement", list(dfs.keys()), key="selectbox_tab1")
        df_selected = dfs[evenement]
        afficher_tweets_gravite(df_selected)
        afficher_gravite_plotly(df_selected, f"pour {evenement.lower()}")

    with tab2:
        st.header("Gravité pour un Event ID spécifique")
        eventids = sorted(df_event['crise_id'].astype(str).unique())
        selected_eventid = st.selectbox('Sélectionne un Event ID', eventids, key="selectbox_tab2")
        df_selected = df_event[df_event['crise_id'].astype(str) == selected_eventid]
        afficher_tweets_gravite(df_selected)
        afficher_gravite_event_plotly(df_event)

    with tab3:
        st.header("Analyse de la Gravité par Catégorie de Post")
        selected_category = st.selectbox(
            "Sélectionne une catégorie de post",
            df_categories['category_label'].unique(),
            key="selectbox_tab3"
        )
        tweets = df_categories[df_categories['category_label'] == selected_category]
        with st.expander("📃 Aperçu de quelques tweets classés par gravité"):
            col_low, col_medium, col_high, col_critical = st.columns(4)
            gravite_niveaux = ["Low", "Medium", "High", "Critical"]
            colonnes = {
                "Low": col_low,
                "Medium": col_medium,
                "High": col_high,
                "Critical": col_critical
            }
            for gravite in gravite_niveaux:
                with colonnes[gravite]:
                    st.markdown(f"### {gravite}")
                    subset = tweets[tweets["annotation_postPriority"] == gravite].head(3)
                    for _, row in subset.iterrows():
                        texte = row.get("text", "")
                        couleur = gravite_couleurs.get(gravite, "#f0f0f0")
                        st.markdown(
                            f"""
                            <div style="background-color:{couleur}; padding: 10px; border-radius: 10px; margin-bottom:10px; border: 1px solid #ccc;">
                                <p style="margin: 0; font-size: 14px;color: black">{texte}</p>
                            </div>""",
                            unsafe_allow_html=True
                        )
        afficher_gravite_par_categorie(df_categories)

    with tab4:
        st.header("Top mots ou hashtags des tweets à gravité élevée")
        evenement = st.selectbox("Sélectionnez un événement pour le Wordcloud", list(dfs.keys()), key="selectbox_tab4")
        df_selected = dfs[evenement]
        afficher_tweets_gravite(df_selected[df_selected["annotation_postPriority"].isin(["High", "Critical"])])
        afficher_wordcloud_gravite(df_selected)
