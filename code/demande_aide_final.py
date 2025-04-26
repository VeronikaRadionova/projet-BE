import streamlit as st
import plotly.express as px
import pandas as pd
def demande_aide(dataframes, labels):
    st.title("📊 Analyse des tweets par crise")

    # --- Chargement depuis menu.py ---
    tweets = dataframes["Tweet_date_clean"]
    is_about = dataframes["is_about_clean"]
    events = dataframes["Event_clean"]
    help_requests = dataframes["help_requests"]

    # --- Normalisation ---
    tweets['tweet_id'] = tweets['tweet_id'].astype(str)
    is_about['tweet_id'] = is_about['tweet_id'].astype(str)
    help_requests['tweet_id'] = help_requests['tweet_id'].astype(str)
    events['event_id'] = events['event_id'].astype(str)
    is_about['event_id'] = is_about['event_id'].astype(str)

    # --- Corriger les event_id numériques ---
    event_id_map = dict(zip(events.index.astype(str), events['event_id']))
    is_about['event_id'] = is_about['event_id'].map(event_id_map)

    # --- Fusion ---
    merged = tweets.merge(is_about, on="tweet_id", how="inner")
    merged = merged.merge(events[['event_id', 'event_type']], on="event_id", how="left")
    merged = merged.merge(help_requests[['tweet_id', 'category_name']], on="tweet_id", how="left")
    merged['created_at'] = pd.to_datetime(merged['created_at'], errors='coerce')
    merged['is_help'] = merged['category_name'].notna()

    # --- Filtres dans la page ---
    st.markdown("### 🎯 Filtrer par événement")
    event_options = merged['event_id'].dropna().unique()
    selected_event_id = st.selectbox("Choisissez un événement spécifique :", ["Tous"] + sorted(event_options))

    if selected_event_id != "Tous":
        merged = merged[merged['event_id'] == selected_event_id]

    # --- Menu d'analyse ---
    st.markdown("### 🧭 Menu d'analyse")
    col1, col2, col3 = st.columns(3)
    view_tweet_stats = col1.checkbox("📌 Statistiques globales", True)
    view_help_proportion = col2.checkbox("🆘 % d'aide", False)
    view_help_vs_total = col3.checkbox("🔁 Aide vs total", False)

    col4, col5 = st.columns(2)
    view_category_distribution = col4.checkbox("📂 Types d'aide", False)
    view_timeline = col5.checkbox("📅 Timeline", False)

    view_sensitive = st.checkbox("🚨 Contenu sensible", False)

    if view_tweet_stats:
        st.subheader("📌 Nombre total de tweets par crise")
        tweet_counts = merged['event_id'].value_counts().reset_index()
        tweet_counts.columns = ['event_id', 'nb_tweets']
        tweet_counts = tweet_counts.merge(events[['event_id', 'event_type']], on="event_id", how="left")

        fig1 = px.bar(tweet_counts, x="event_type", y="nb_tweets", text="nb_tweets",
                      labels={"event_type": "Type de crise", "nb_tweets": "Tweets"},
                      title="Nombre total de tweets par type de crise")
        fig1.update_traces(textposition="outside")
        st.plotly_chart(fig1, use_container_width=True)

    if view_help_proportion:
        st.subheader("🆘 Proportion de tweets d'aide par crise")
        help_stats = merged.groupby('event_type')['is_help'].mean().reset_index(name='pourcentage_aide')
        help_stats['pourcentage_aide'] *= 100

        fig2 = px.bar(help_stats, x="event_type", y="pourcentage_aide",
                      labels={"event_type": "Type de crise", "pourcentage_aide": "% Aide"},
                      title="Part des tweets d'aide par type de crise")
        fig2.update_traces(texttemplate='%{y:.1f}%', textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    if view_help_vs_total:
        st.subheader("🔁 Tweets totaux vs. tweets d'aide par crise")
        help_counts = merged.groupby(['event_type', 'is_help']).size().reset_index(name='count')
        help_counts['type'] = help_counts['is_help'].map({True: 'Aide', False: 'Autres'})

        fig6 = px.bar(help_counts, x='event_type', y='count', color='type',
                      barmode='stack', text='count',
                      title="Volume de tweets d'aide vs. autres par type de crise",
                      labels={'event_type': 'Crise', 'count': 'Tweets', 'type': 'Type'})
        st.plotly_chart(fig6, use_container_width=True)

    if view_category_distribution:
        st.subheader("📂 Répartition des types d'aide par crise")
        crises = merged['event_type'].dropna().unique()
        selected_crise = st.selectbox("Choisir une crise :", sorted(crises))
        crise_filtered = merged[(merged['event_type'] == selected_crise) & (merged['is_help'])]

        if not crise_filtered.empty:
            cat_counts = crise_filtered['category_name'].value_counts().reset_index()
            cat_counts.columns = ['category', 'count']
            fig3 = px.pie(cat_counts, names='category', values='count', title=f"Répartition des demandes pour {selected_crise}")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Aucune donnée d'aide pour cette crise.")

    if view_timeline:
        st.subheader("📅 Évolution des tweets par jour")
        daily_stats = merged.groupby([merged['created_at'].dt.date, 'event_type']).size().reset_index(name='tweets')
        fig4 = px.line(daily_stats, x="created_at", y="tweets", color="event_type",
                       title="Nombre de tweets par jour et par crise",
                       labels={"created_at": "Date", "tweets": "Tweets", "event_type": "Crise"})
        st.plotly_chart(fig4, use_container_width=True)

    if view_sensitive:
        st.subheader("🚨 Proportion de contenu sensible")
        sensitive_stats = merged.groupby('event_type')['possibly_sensitive'].mean().reset_index()
        sensitive_stats['possibly_sensitive'] *= 100
        fig5 = px.bar(sensitive_stats, x="event_type", y="possibly_sensitive",
                      labels={"possibly_sensitive": "% sensible", "event_type": "Crise"},
                      title="Proportion de contenu sensible par type de crise")
        fig5.update_traces(texttemplate='%{y:.1f}%', textposition="outside")
        st.plotly_chart(fig5, use_container_width=True)
