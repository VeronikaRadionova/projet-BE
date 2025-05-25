import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

def create_heatmap(df):
    geo_df = df.dropna(subset=['latitude', 'longitude'])

    if geo_df.empty:
        st.warning("Aucune donnée géolocalisée trouvée.")
        return

    map_center = [geo_df['latitude'].mean(), geo_df['longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=4)

    # Ajout de la HeatMap
    heat_data = geo_df[['latitude', 'longitude']].values.tolist()
    HeatMap(heat_data, radius=15).add_to(m)

    # Ajouter des marqueurs pour chaque crise
    df_points = geo_df.drop_duplicates(subset="topic")
    for _, row in df_points.iterrows():
        topic = row["topic"]
        crisis_df = geo_df[geo_df["topic"] == topic]
        n_tweets = len(crisis_df)
        n_positif = crisis_df[crisis_df["sentiment"] == "positive"].shape[0]
        p_positif = (n_positif / n_tweets) * 100 if n_tweets > 0 else 0
        exemple = crisis_df["text"].dropna().iloc[0][:100] + "..."
        popup_content = f"""
        <b>📌 Crise :</b> {topic}<br>
        <b>🔢 Tweets :</b> {n_tweets}<br>
        <b>🙂 % Positifs :</b> {p_positif:.1f}%<br>
        <b>💬 Exemple :</b> {exemple}
        """

        # Ici, on ajoute plus d'informations au tooltip
        tooltip_content = f"""
        <b>📌 Crise :</b> {topic}<br>
        """

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=3,
            color="black",
            fill=True,
            fill_opacity=0.5,
            tooltip=folium.Tooltip(tooltip_content),  # Ajout d'informations supplémentaires au survol
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(m)

    # Affichage dans Streamlit
    st_folium(m, use_container_width=True, height=600)

def afficher_statistiques_temps(df):
    # --- 📈 Évolution des tweets dans le temps par topic ---

    # Vérifiez que les colonnes 'created_at' et 'topic' sont présentes
    if "created_at" in df.columns and "topic" in df.columns:
        df["date"] = df["created_at"].dt.date  # Extraire uniquement la date
        tweets_per_day_topic = df.groupby(["date", "topic"]).size().reset_index(name="Nombre_de_tweets")

        fig_time = px.line(
            tweets_per_day_topic,
            x="date",
            y="Nombre_de_tweets",
            color="topic",
            title="Évolution des tweets dans le temps par topic",
            labels={"date": "Date", "Nombre_de_tweets": "Nombre de Tweets", "topic": "Topic"},
            markers=True
        )
        fig_time.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="Nombre de Tweets")
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.warning("Les colonnes 'created_at' ou 'topic' sont manquantes ou mal formatées.")

def afficherHashtag(dataframes, readable_topics=None):
    # Vérifie la présence du fichier nécessaire
    if "Hashtag_clean" not in dataframes:
        st.error("Le fichier 'Hashtag_clean.csv' est manquant dans le dossier CSV.")
        return

    df = dataframes["Hashtag_clean"]

    # Vérification des colonnes nécessaires
    required_columns = {"hashtag_id", "occurences", "topic"}
    if not required_columns.issubset(df.columns):
        st.error("Colonnes attendues manquantes dans le DataFrame (besoin de 'hashtag_id', 'occurences', 'topic').")
        return

    # Nettoyage des hashtags
    df['hashtag_id'] = df['hashtag_id'].astype(str).str.lower().str.strip()
    df['topic'] = df['topic'].astype(str).str.strip()

    # Grouper par hashtag et crise
    hashtag_crise_counts = df.groupby(['hashtag_id', 'topic'])["occurences"].sum().reset_index()
    # Remplacer les topics par leur nom lisible si fourni
    if readable_topics:
        hashtag_crise_counts['topic'] = hashtag_crise_counts['topic'].map(readable_topics).fillna(hashtag_crise_counts['topic'])

    # Pour chaque hashtag, lister les crises associées (pour affichage dans le tableau)
    hashtag_to_crises = hashtag_crise_counts.groupby('hashtag_id')['topic'].apply(lambda x: ', '.join(sorted(set(x)))).reset_index()
    hashtag_to_crises.columns = ['hashtag_id', 'crises']

    # Total occurrences par hashtag (toutes crises confondues)
    total_counts = hashtag_crise_counts.groupby('hashtag_id')["occurences"].sum().reset_index()
    total_counts = total_counts.sort_values(by='occurences', ascending=False)

    # Fusion pour affichage tableau
    table = total_counts.merge(hashtag_to_crises, on='hashtag_id')

    # Slider interactif
    max_n = min(30, len(table))
    if max_n < 5:
        st.info("Moins de 5 hashtags trouvés dans les données.")
        top_n = max_n
    else:
        top_n = st.slider("Nombre de hashtags à afficher", min_value=5, max_value=max_n, value=min(10, max_n), key="slider_hashtag_crise")

    # Affichage du graphique barres groupées par crise
    top_hashtags = table.head(top_n)['hashtag_id'].tolist()
    df_plot = hashtag_crise_counts[hashtag_crise_counts['hashtag_id'].isin(top_hashtags)]
    fig = px.bar(
        df_plot,
        x='occurences',
        y='hashtag_id',
        color='topic',
        orientation='h',
        title=f"Top {top_n} hashtags par crise",
        labels={'occurences': 'Nombre d’occurrences', 'hashtag_id': 'Hashtag', 'topic': 'Crise'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    # Affichage du tableau hashtags + crises associées
    st.markdown("**Tableau des hashtags et crises associées :**")
    st.dataframe(table.head(top_n), use_container_width=True)

def afficher_repartition_par_topic(df):
    # --- 🥧 Répartition des tweets par topic ---
    st.subheader("📚 Répartition des tweets par topic")

    # Vérifier que la colonne 'topic' est présente
    if "topic" not in df.columns:
        st.warning("La colonne 'topic' est manquante dans le DataFrame.")
        return

    # Comptage des tweets par topic
    topic_counts = df["topic"].value_counts().reset_index()
    topic_counts.columns = ["Topic", "Nombre_de_tweets"]

    # --- 📊 Graphique Barres ---
    fig_topic_bar = px.bar(
        topic_counts,
        x="Topic",
        y="Nombre_de_tweets",
        text_auto=True,
        title="Répartition des tweets par topic",
        labels={"Topic": "Topic", "Nombre_de_tweets": "Nombre de Tweets"}
    )
    fig_topic_bar.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig_topic_bar, use_container_width=True)

    # --- 🥧 Graphique Camembert ---
    fig_topic_pie = px.pie(
        topic_counts,
        values="Nombre_de_tweets",
        names="Topic",
        title="Répartition des tweets par topic",
        hole=0.4
    )
    fig_topic_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_topic_pie, use_container_width=True)

def afficherTimeline(data):
    st.subheader("📅 Évolution des tweets par jour")
    daily_stats = data.groupby([data['created_at'].dt.date, 'event_type']).size().reset_index(name='tweets')
    fig4 = px.line(daily_stats, x="created_at", y="tweets", color="event_type",
                    title="Nombre de tweets par jour et par crise",
                    labels={"created_at": "Date", "tweets": "Tweets", "event_type": "Crise"})
    st.plotly_chart(fig4, use_container_width=True)


#TODO debugger
def afficherInfluenceur(dataframes,selected_label):
    tweets = dataframes["Tweet_date_clean"]
    is_about = dataframes["is_about_clean"]
    posted = dataframes["posted_clean"]
    users = dataframes["User_clean"]
    reply_user = dataframes["reply_tweet_to_user"]

    for df in [tweets, is_about, posted]:
        df['tweet_id'] = df['tweet_id'].astype(str)
    users['user_id'] = users['user_id'].astype(str)
    reply_user['end_id'] = reply_user['end_id'].astype(str)

    tweets_base = tweets.merge(posted, on="tweet_id", how="left").merge(is_about, on="tweet_id", how="left")

    if 'reply_count' not in tweets_base.columns:
        tweets_base['reply_count'] = 0

    tweets_base = tweets_base[tweets_base['event_id'] == selected_label]

    engagement = tweets_base.groupby('user_id').agg({
        'tweet_id': 'count',
        'retweet_count': 'sum',
        'reply_count': 'sum'
    }).reset_index()

    engagement.rename(columns={
        'tweet_id': 'nb_tweets',
        'retweet_count': 'total_retweets',
        'reply_count': 'total_replies'
    }, inplace=True)

    engagement['user_id'] = engagement['user_id'].astype(str)

    replies_received = reply_user['end_id'].value_counts().reset_index()
    replies_received.columns = ['user_id', 'nb_replies_received']

    engagement = engagement.merge(replies_received, on='user_id', how='left')
    engagement['nb_replies_received'] = engagement['nb_replies_received'].fillna(0)

    # Score d'engagement
    engagement['engagement_score'] = engagement['total_retweets'] + engagement['nb_replies_received']
    engagement['retweet_ratio'] = engagement['total_retweets'] / engagement['nb_tweets']

    engagement = engagement.merge(users[['user_id', 'screen_name', 'followers_count']], on='user_id', how='left')
    engagement['event_name'] = selected_label  # on l’ajoute ici pour affichage

    # Affichage
    st.markdown(f"### Influenceurs les plus influent sur {selected_label}")
    if not engagement.empty:
        total_influenceurs = engagement['user_id'].nunique()
        best_user = engagement.sort_values(by='engagement_score', ascending=False).iloc[0]
        st.metric("Nombre total d'influenceurs recensés sur la crise", total_influenceurs)


    top_users = engagement.sort_values(by='engagement_score', ascending=False).head(10)

    if not top_users.empty:
        fig = px.bar(
            top_users,
            x='screen_name',
            y='engagement_score',
            text='engagement_score',
            color='event_name',
            hover_data=['nb_tweets', 'total_retweets', 'nb_replies_received', 'followers_count', 'retweet_ratio'],
            title=f"Score d'engagement",
            labels={"screen_name": "Utilisateur", "engagement_score": "Score", "event_name": "Crise"}
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Distribution du ratio retweets / tweets")
        fig_ratio = px.histogram(
            top_users,
            x='retweet_ratio',
            nbins=20,
            title="Répartition du ratio retweets/tweet",
            labels={"retweet_ratio": "Ratio"}
        )
        st.plotly_chart(fig_ratio, use_container_width=True)



def afficherLocalisation(df):

    df_geo = df.dropna(subset=["latitude", "longitude", "retweet_count", "sentiment", "text"])
    df_geo = df_geo[(df_geo["latitude"] != 0) & (df_geo["longitude"] != 0)]

    if df_geo.empty:
        st.warning("Aucun tweet géolocalisé trouvé.")
        return


    # Filtrer par nombre minimal de retweets

    if df_geo.empty:
        st.warning("Aucun tweet ne correspond au seuil de retweets.")
        return

    # Ajouter un jitter pour éviter le chevauchement
    np.random.seed(42)
    df_geo["latitude_jitter"] = df_geo["latitude"] + np.random.uniform(-0.01, 0.01, size=len(df_geo))
    df_geo["longitude_jitter"] = df_geo["longitude"] + np.random.uniform(-0.01, 0.01, size=len(df_geo))

    df_geo["taille_point"] = df_geo["retweet_count"].apply(lambda x: max(5, min(x * 0.5, 40)))


    
    fig = px.scatter_mapbox(
        df_geo,
        lat="latitude",
        lon="longitude",
        # hover_name="text",
        # hover_data={"retweet_count": True, "sentiment": True},
        size="taille_point",
        color="sentiment",
        color_discrete_map={
            "positive": "green",
            "neutral": "gray",
            "negative": "red"
        },
        zoom=2,
        height=700
    )

    # Layout final
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            zoom=2,
            center=dict(
                lat=df_geo["latitude"].mean(),
                lon=df_geo["longitude"].mean()
            )
        ),
        height=700,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    st.plotly_chart(fig, use_container_width=True)

def afficherTopHashtagParCriseFromList(df, selected_topic, readable_topics=None):
    """
    Affiche le top des hashtags pour une crise sélectionnée à partir d'une colonne de listes de hashtags.
    df : DataFrame contenant au moins les colonnes 'topic' et 'hashtags' (liste ou str de liste)
    selected_topic : nom ou identifiant de la crise à filtrer
    readable_topics : dict optionnel pour afficher le nom lisible de la crise
    """
    # Déterminer le nom lisible de la crise
    nom_crise = readable_topics[selected_topic] if readable_topics and selected_topic in readable_topics else selected_topic
    st.subheader(f"🏷️ Top hashtags pour la crise : {nom_crise}")

    # Filtrer sur la crise sélectionnée
    df_crise = df[df["topic"] == selected_topic].copy()
    if df_crise.empty:
        st.info(f"Aucun tweet trouvé pour la crise : {nom_crise}")
        return

    # S'assurer que 'hashtags' est une liste
    df_crise['hashtags'] = df_crise['hashtags'].apply(
        lambda x: eval(x) if isinstance(x, str) and x not in ["", "nan", "None"] else x
    )
    df_exploded = df_crise.explode('hashtags')

    # Nettoyage
    df_exploded = df_exploded.dropna(subset=['hashtags'])
    df_exploded['hashtags'] = df_exploded['hashtags'].astype(str).str.lower().str.strip()
    df_exploded = df_exploded[df_exploded['hashtags'] != ""]

    # Comptage des hashtags
    hashtag_counts = df_exploded['hashtags'].value_counts().reset_index()
    hashtag_counts.columns = ['hashtag', 'occurences']

    if hashtag_counts.empty:
        st.info(f"Aucun hashtag trouvé pour la crise : {nom_crise}")
        return

    # Adapter la borne max du slider au nombre de hashtags disponibles
    max_n = min(30, len(hashtag_counts))
    if max_n < 5:
        st.info(f"Moins de 5 hashtags trouvés pour la crise : {nom_crise}")
        top_n = max_n
    else:
        top_n = st.slider(f"Nombre de hashtags à afficher pour {nom_crise}", min_value=5, max_value=max_n, value=min(10, max_n), key=f"slider_list_{selected_topic}")

    # Affichage du graphique
    fig = px.bar(
        hashtag_counts.head(top_n),
        x='occurences',
        y='hashtag',
        orientation='h',
        title=f"Top {top_n} hashtags pour {nom_crise}",
        labels={'occurences': 'Nombre d’occurrences', 'hashtag': 'Hashtag'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

def afficherHashtag(df, readable_topics=None):
    """
    Affiche le top des hashtags de toutes les crises, avec la/les crises associées à chaque hashtag.
    df : DataFrame contenant au moins les colonnes 'topic' et 'hashtags' (liste ou str de liste)
    readable_topics : dict optionnel pour afficher le nom lisible de la crise
    """
    df = df.copy()
    # S'assurer que 'hashtags' est une liste
    def to_list(x):
        if isinstance(x, list):
            return x
        if isinstance(x, str) and x not in ["", "nan", "None"]:
            try:
                val = eval(x)
                if isinstance(val, list):
                    return val
                return [val]
            except:
                return [x]
        return []
    df['hashtags'] = df['hashtags'].apply(to_list)
    df_exploded = df.explode('hashtags')

    # Nettoyage
    df_exploded = df_exploded.dropna(subset=['hashtags', 'topic'])
    df_exploded['hashtags'] = df_exploded['hashtags'].astype(str).str.lower().str.strip()
    df_exploded['topic'] = df_exploded['topic'].astype(str).str.strip()
    df_exploded = df_exploded[df_exploded['hashtags'] != ""]

    # Remplacer les topics par leur nom lisible si fourni
    if readable_topics:
        df_exploded['topic'] = df_exploded['topic'].map(readable_topics).fillna(df_exploded['topic'])

    # Grouper par hashtag et crise
    hashtag_crise_counts = df_exploded.groupby(['hashtags', 'topic']).size().reset_index(name='occurences')

    # Pour chaque hashtag, lister les crises associées (pour affichage dans le tableau)
    hashtag_to_crises = hashtag_crise_counts.groupby('hashtags')['topic'].apply(lambda x: ', '.join(sorted(set(x)))).reset_index()
    hashtag_to_crises.columns = ['hashtag', 'crises']

    # Total occurrences par hashtag (toutes crises confondues)
    total_counts = hashtag_crise_counts.groupby('hashtags')["occurences"].sum().reset_index()
    total_counts = total_counts.sort_values(by='occurences', ascending=False)
    total_counts = total_counts.rename(columns={'hashtags': 'hashtag'})

    # Fusion pour affichage tableau
    table = total_counts.merge(hashtag_to_crises, on='hashtag')

    # Slider interactif
    max_n = min(30, len(table))
    if max_n < 5:
        st.info("Moins de 5 hashtags trouvés dans les données.")
        top_n = max_n
    else:
        top_n = st.slider("Nombre de hashtags à afficher", min_value=5, max_value=max_n, value=min(10, max_n), key="slider_hashtag_crise_all")

    # Affichage du graphique barres groupées par crise
    top_hashtags = table.head(top_n)['hashtag'].tolist()
    df_plot = hashtag_crise_counts[hashtag_crise_counts['hashtags'].isin(top_hashtags)]
    fig = px.bar(
        df_plot,
        x='occurences',
        y='hashtags',
        color='topic',
        orientation='h',
        title=f"Top {top_n} hashtags (toutes crises)",
        labels={'occurences': 'Nombre d’occurrences', 'hashtags': 'Hashtag', 'topic': 'Crise'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    # Affichage du tableau hashtags + crises associées
    st.markdown("**Tableau des hashtags et crises associées :**")
    st.dataframe(table.head(top_n), use_container_width=True)
