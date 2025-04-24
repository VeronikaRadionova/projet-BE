import streamlit as st
import pandas as pd

def recherche_personnalisee():
    st.title("🔎 Recherche personnalisée dans les tweets")

    try:
        df = pd.read_csv("../CSV/Tweet_sentiment_localisation.csv", parse_dates=["created_at"])
    except FileNotFoundError:
        st.error("Fichier Tweet_sentiment_localisation.csv introuvable.")
        return

    st.markdown("Filtre les tweets selon tes propres critères 👇")

    # Filtrage par mot-clé
    keyword = st.text_input("🔤 Contient le mot-clé :")
    if keyword:
        df = df[df["text"].str.contains(keyword, case=False, na=False)]

    # Filtrage par date
    min_date = df["created_at"].min().date()
    max_date = df["created_at"].max().date()
    date_range = st.slider("📅 Plage de dates :", min_value=min_date, max_value=max_date,
                           value=(min_date, max_date))
    df = df[(df["created_at"].dt.date >= date_range[0]) & (df["created_at"].dt.date <= date_range[1])]

    # Filtrage par lieu
    lieux = df["lieu_extrait"].dropna().unique()
    lieux_selectionnes = st.multiselect("📍 Lieu :", options=sorted(lieux))
    if lieux_selectionnes:
        df = df[df["lieu_extrait"].isin(lieux_selectionnes)]

    # Filtrage par sentiment
    sentiments = df["sentiment"].dropna().unique()
    sentiments_selectionnes = st.multiselect("🎭 Sentiment :", options=sorted(sentiments))
    if sentiments_selectionnes:
        df = df[df["sentiment"].isin(sentiments_selectionnes)]

    # Affichage
    st.markdown(f"📄 **{len(df)} tweets** trouvés avec ces filtres.")
    st.dataframe(df[["created_at", "text", "sentiment", "lieu_extrait", "topic"]].sort_values("created_at", ascending=False), use_container_width=True)

    # Export CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Télécharger les résultats", data=csv, file_name="tweets_filtrés.csv", mime="text/csv")
