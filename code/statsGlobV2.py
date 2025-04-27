import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px


def afficher_statistiques_globales():
    st.title("📊 Statistiques globales")

    try:
        df = pd.read_csv("../CSV/Tweet_sentiment_localisation.csv", parse_dates=["created_at"])
    except FileNotFoundError:
        st.error("Fichier Tweet_sentiment_localisation.csv introuvable.")
        return
    

    #Chargement des données
    total_tweets = len(df)
    date_min = df["created_at"].min().date()
    date_max = df["created_at"].max().date()
    nb_topics = df["topic"].nunique()
    total_retweets = int(df["retweet_count"].sum())
    total_likes = int(df["favorite_count"].sum())
    nb_annotated = df["annotation_annotated"].sum()
    nb_high_priority = df[df["annotation_postPriority"] == "High"].shape[0]
    nb_sensitive = df["possibly_sensitive"].sum()

    #Affichage des données
    col1,col2,col3= st.columns(3)

    with col1:
        st.write("🐤 Tweets au total", f"{total_tweets:n}")
        st.write("🗓️ Période couverte", f"{date_min} → {date_max}")
        st.write("🔥 Crises détectées", f"{nb_topics}")    
        st.write("🔁 Retweets totaux", f"{total_retweets:n}")
        st.write("❤️ Likes totaux", f"{total_likes:n}")
        st.write("🚨 Tweets sensibles", f"{int(nb_sensitive)}")
        st.write("📌 Tweets annotés : {int(nb_annotated)}")
        st.write("📌 Tweets de priorité haute : {nb_high_priority}")
    with col2:
        afficher_statistiques_temps(df)
    with col3:
        create_heatmap(df)

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
        topic = row["topic"] #TODO changer les TRECIS en nom de crises
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