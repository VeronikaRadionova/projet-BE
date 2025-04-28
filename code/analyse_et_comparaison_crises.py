import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def analyse_complete_crise(dataframes, labels):
    st.title("🔎 Analyse et suivi d'une crise : Volume & Sentiments")

    if "Tweet_sentiment_localisation" not in dataframes:
        st.error("Le fichier 'Tweet_sentiment_localisation.csv' est manquant.")
        return

    df = dataframes["Tweet_sentiment_localisation"]
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    
    label_to_code = {v: k for k, v in labels.items()}
    code_to_label = {k: v for k, v in labels.items()}

    crises_codes = df["topic"].dropna().unique()
    crises_lisibles = [labels.get(code, code) for code in sorted(crises_codes)]

    selected_label = st.selectbox("📍 Choisissez une crise :", crises_lisibles)
    selected_code = label_to_code.get(selected_label, selected_label)

    df_crisis = df[df["topic"] == selected_code]

    if df_crisis.empty:
        st.warning("Aucun tweet disponible pour cette crise.")
        return

    # Informations générales ---
    with st.expander("📋 Informations générales sur la crise"):
        st.markdown(f"- **Crise sélectionnée** : {selected_label}")
        st.markdown(f"- **Nombre de tweets** : {len(df_crisis)}")
        dernier_tweet = df_crisis["created_at"].max()
        if pd.notnull(dernier_tweet):
            st.markdown(f"- **Dernier tweet** : {dernier_tweet.strftime('%Y-%m-%d %H:%M')}")

    # Aperçu des tweets ---
    with st.expander("📝 Tweets récents"):
        for _, row in df_crisis.sort_values("created_at", ascending=False).head(10).iterrows():
            st.markdown(f"📅 *{row['created_at']}* – ❤️ {row['favorite_count']} – 🔁 {row['retweet_count']}")
            st.markdown(f"> {row['text']}")
            st.markdown("---")

    # Fréquence des tweets ---
    with st.expander("📈 Volume de tweets dans le temps"):
        df_crisis["date"] = df_crisis["created_at"].dt.date
        freq = df_crisis.groupby("date").size().reset_index(name="nb_tweets")
        fig_freq = px.line(freq, x="date", y="nb_tweets", markers=True, title="Évolution du volume de tweets")
        st.plotly_chart(fig_freq, use_container_width=True)
        st.subheader("📊 Données journalières")
        tweet_counts = df_crisis.groupby('date').size().reset_index(name='Nombre de tweets')
        st.dataframe(tweet_counts, use_container_width=True)

    # Répartition des sentiments ---
    with st.expander("🎭 Répartition des sentiments"):
        set3_colors = px.colors.qualitative.Set3
        color_map = {
            'positive': set3_colors[1],
            'neutral': set3_colors[0],
            'negative': set3_colors[2]
        }

        roberta_counts = df_crisis['sentiment'].value_counts().reset_index()
        roberta_counts.columns = ['Sentiment', 'Tweets']

        fig_bar = px.bar(
            roberta_counts,
            x='Sentiment',
            y='Tweets',
            color='Sentiment',
            color_discrete_map=color_map,
            title="Distribution des sentiments"
        )
        fig_bar.update_layout(barmode='stack')

        value_counts = df_crisis['sentiment'].value_counts()
        labels_pie = value_counts.index.tolist()
        values_pie = value_counts.values.tolist()
        donut_colors = [color_map.get(label, '#333333') for label in labels_pie]

        fig_pie = go.Figure(data=[go.Pie(
            labels=labels_pie,
            values=values_pie,
            hole=0.4,
            marker=dict(colors=donut_colors),
            textinfo='percent'
        )])

        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            st.plotly_chart(fig_pie, use_container_width=True)

    # Évolution des sentiments---
    with st.expander("⏳ Sentiment moyen dans le temps"):
        sentiment_map = {'negative': -1, 'neutral': 0, 'positive': 1}
        df_crisis['roberta_score'] = df_crisis['sentiment'].map(sentiment_map)

        daily_sentiment = df_crisis.groupby('date')['roberta_score'].mean().reset_index()

        fig_sentiment = px.line(
            daily_sentiment,
            x='date',
            y='roberta_score',
            title='Évolution du sentiment moyen',
            markers=True,
            labels={'roberta_score': 'Sentiment Moyen (-1 = Négatif, 1 = Positif)', 'date': 'Date'}
        )

        fig_sentiment.update_layout(
            xaxis_title='Date',
            yaxis_title='Sentiment Moyen',
            xaxis_tickangle=-45,
            yaxis=dict(dtick=0.5),
            template='plotly_white'
        )

        st.plotly_chart(fig_sentiment, use_container_width=True)
