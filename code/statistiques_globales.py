import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px


def afficher_statistiques_globales(dataframes, labels):
    st.title("📊 Statistiques globales")

    # Vérification si les données sont présentes
    if "Tweet_sentiment_localisation" not in dataframes:
        st.error("Le fichier 'Tweet_sentiment_localisation.csv' est manquant.")
        return

    # Chargement des données
    df = dataframes["Tweet_sentiment_localisation"]
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["topic"] = df["topic"].map(labels).fillna(df["topic"])

    st.markdown("### Vue d’ensemble des données")

    # Calcul des statistiques globales
    total_tweets = len(df)
    date_min = df["created_at"].min().date()
    date_max = df["created_at"].max().date()
    nb_topics = df["topic"].nunique()
    total_retweets = int(df["retweet_count"].sum())
    total_likes = int(df["favorite_count"].sum())

    nb_annotated = df["annotation_annotated"].sum()
    nb_high_priority = df[df["annotation_postPriority"] == "High"].shape[0]
    nb_sensitive = df["possibly_sensitive"].sum()

    # Affichage des métriques
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
        top_tweet = get_top_tweet(df)
        st.markdown("### 🌟 Tweet le plus populaire")
        st.code(top_tweet["text"], language="markdown")
        st.write(f"Retweets : {top_tweet['retweet_count']} | Likes : {top_tweet['favorite_count']}")

    afficher_statistiques_temps(df)
    # Carte de chaleur géographique des tweets
    if {'latitude', 'longitude'}.issubset(df.columns):
        st.subheader("🌍 Carte de chaleur géographique des tweets + Infos par crise")
        create_heatmap(df)
    else:
        st.warning("Aucune donnée géolocalisée trouvée.")
    

    


def get_top_tweet(df):
    return df.loc[df["retweet_count"].idxmax()]


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
    # --- 📈 Évolution des tweets dans le temps ---
    st.subheader("📅 Évolution des tweets dans le temps")

    # Vérifiez que la colonne 'created_at' est bien au format datetime
    if "created_at" in df.columns:
        df["date"] = df["created_at"].dt.date  # Extraire uniquement la date
        tweets_per_day = df.groupby("date").size().reset_index(name="Nombre_de_tweets")

        fig_time = px.line(
            tweets_per_day,
            x="date",
            y="Nombre_de_tweets",
            title="Évolution du nombre de tweets dans le temps",
            labels={"date": "Date", "Nombre_de_tweets": "Nombre de Tweets"},
            markers=True
        )
        fig_time.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="Nombre de Tweets")
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.warning("La colonne 'created_at' est manquante ou mal formatée.")