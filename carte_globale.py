import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def afficher_carte_globale():
    st.title("🗺️ Carte globale des tweets")

    try:
        df = pd.read_csv("Tweet_sentiment_localisation.csv")
    except FileNotFoundError:
        st.error("Fichier Tweet_sentiment_localisation.csv introuvable.")
        return

    required_cols = {"latitude", "longitude", "retweet_count", "sentiment", "text"}
    if not required_cols.issubset(df.columns):
        st.error("Colonnes nécessaires manquantes dans le fichier.")
        return

    df_geo = df.dropna(subset=["latitude", "longitude", "retweet_count", "sentiment", "text"])
    df_geo = df_geo[(df_geo["latitude"] != 0) & (df_geo["longitude"] != 0)]

    if df_geo.empty:
        st.warning("Aucun tweet géolocalisé à afficher.")
        return

    # Slider pour le filtrage
    min_retweet, max_retweet = int(df_geo["retweet_count"].min()), int(df_geo["retweet_count"].max())
    seuil_retweet = st.slider("🎚️ Nombre minimal de retweets à afficher :", min_value=min_retweet,
                              max_value=max_retweet, value=min_retweet, step=1)

    df_geo = df_geo[df_geo["retweet_count"] >= seuil_retweet]

    if df_geo.empty:
        st.warning("Aucun tweet ne correspond au seuil de retweets sélectionné.")
        return

    # Jitter sur coordonnées
    np.random.seed(42)
    df_geo["latitude_jitter"] = df_geo["latitude"] + np.random.uniform(-0.01, 0.01, size=len(df_geo))
    df_geo["longitude_jitter"] = df_geo["longitude"] + np.random.uniform(-0.01, 0.01, size=len(df_geo))

    # Taille de points
    df_geo["taille_point"] = df_geo["retweet_count"].apply(lambda x: max(5, min(x * 0.5, 40)))

    # Vue sélectionnable
    vue = st.radio("🗺️ Choisir la vue :", [
        "📍 Carte des tweets (points)",
        "🔥 Heatmap simple (densité brute)",
        "🔥 Heatmap pondérée (par retweets)" #Pas sûr de celle-là
    ])

    if vue == "📍 Carte des tweets (points)":
        st.markdown("**🧭 Zoom sur les tweets géolocalisés : taille = retweets, couleur = sentiment**")
        fig = px.scatter_mapbox(
            df_geo,
            lat="latitude",
            lon="longitude",
            hover_name="text",
            hover_data={"retweet_count": True, "sentiment": True},
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

    elif vue == "🔥 Heatmap simple (densité brute)":
        st.markdown("**🔸 Plus c'est chaud, plus il y a de tweets dans la zone**")
        fig = go.Figure()
        fig.add_trace(go.Densitymapbox(
            lat=df_geo["latitude_jitter"],
            lon=df_geo["longitude_jitter"],
            radius=30,
            colorscale="YlOrRd",
            showscale=True,
            hoverinfo='skip'
        ))

    elif vue == "🔥 Heatmap pondérée (par retweets)":
        st.markdown("**🔸 Plus c'est chaud, plus les tweets sont retweetés dans la zone**")
        fig = go.Figure()
        fig.add_trace(go.Densitymapbox(
            lat=df_geo["latitude_jitter"],
            lon=df_geo["longitude_jitter"],
            z=df_geo["retweet_count"],
            radius=30,
            colorscale="YlGnBu",
            showscale=True,
            hoverinfo='skip'
        ))

    # Layout final
    if vue.startswith("🔥"):
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
    else:
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    st.plotly_chart(fig, use_container_width=True)
