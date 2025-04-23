import streamlit as st
import pandas as pd
import plotly.express as px


def top_influenceurs():
    st.title(" Top Influenceurs par Crise (Retweets + Réponses)")

    # --- Chargement des fichiers ---
    tweets = pd.read_csv("Tweet_date_clean.csv")
    is_about = pd.read_csv("is_about_clean.csv")
    posted = pd.read_csv("posted_clean.csv")
    users = pd.read_csv("User_clean.csv")

    # --- Normalisation ---
    for df in [tweets, is_about, posted]:
        df['tweet_id'] = df['tweet_id'].astype(str)
    users['user_id'] = users['user_id'].astype(str)

    # --- Fusion : tweet → user → event
    tweets_base = tweets.merge(posted, on="tweet_id", how="left").merge(is_about, on="tweet_id", how="left")

    # --- Gestion fallback si pas de 'reply_count'
    if 'reply_count' not in tweets_base.columns:
        tweets_base['reply_count'] = 0

    # --- Stats par user_id + event_id
    engagement = tweets_base.groupby(['user_id', 'event_id']).agg({
        'tweet_id': 'count',
        'retweet_count': 'sum',
        'reply_count': 'sum'
    }).reset_index()

    engagement.rename(columns={
        'tweet_id': 'nb_tweets',
        'retweet_count': 'total_retweets',
        'reply_count': 'total_replies'
    }, inplace=True)

    # --- Score global + ratio
    engagement['engagement_score'] = engagement['total_retweets'] + engagement['total_replies']
    engagement['retweet_ratio'] = engagement['total_retweets'] / engagement['nb_tweets']

    # --- Fusion avec les infos utilisateurs ---
    engagement['user_id'] = engagement['user_id'].astype(str)
    engagement = engagement.merge(users[['user_id', 'screen_name', 'followers_count']], on='user_id', how='left')

    # --- Statistiques générales ---
    st.markdown("###  Statistiques Générales")
    total_influenceurs = engagement['user_id'].nunique()
    best_user = engagement.sort_values(by='engagement_score', ascending=False).iloc[0]
    st.metric(label="Nombre total d'influenceurs (toutes crises)", value=total_influenceurs)
    st.metric(label="Meilleur influenceur", value=f"{best_user['screen_name']} ({int(best_user['engagement_score'])} points)")

    # --- Menu latéral ---
    st.sidebar.title(" Filtres")
    event_list = sorted(engagement['event_id'].dropna().unique())
    selected_events = st.sidebar.multiselect("Choisir une ou plusieurs crises (event_id) :", event_list, default=event_list[:1])
    top_n = st.sidebar.slider("Nombre de top utilisateurs :", 5, 30, 10)
    min_retweets = st.sidebar.number_input(" Minimum de retweets", min_value=0, value=0)
    min_followers = st.sidebar.number_input(" Minimum de followers", min_value=0, value=0)

    # --- Filtrage par crises et seuils ---
    filtered = engagement[(engagement['event_id'].isin(selected_events)) &
                          (engagement['total_retweets'] >= min_retweets) &
                          (engagement['followers_count'] >= min_followers)].copy()

    # --- Top N ---
    top_users = filtered.sort_values(by='engagement_score', ascending=False).head(top_n)

    # --- Affichage graphique ---
    st.subheader(f" Top {top_n} influenceurs – Crises sélectionnées")
    fig = px.bar(
        top_users,
        x='screen_name',
        y='engagement_score',
        text='engagement_score',
        color='event_id',
        hover_data=['nb_tweets', 'total_retweets', 'total_replies', 'followers_count', 'retweet_ratio'],
        title="Score d'engagement (retweets + replies)",
        labels={"screen_name": "Utilisateur", "engagement_score": "Score d'engagement"}
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # --- Histogramme des ratios retweet/tweet ---
    st.subheader(" Ratio retweets / tweets")
    fig_ratio = px.histogram(
        top_users,
        x='retweet_ratio',
        nbins=20,
        title="Distribution du ratio retweets / tweets",
        labels={'retweet_ratio': 'Ratio retweets/tweet'}
    )
    st.plotly_chart(fig_ratio, use_container_width=True)

    # --- Détails des influenceurs ---
    st.subheader(" Détail des influenceurs")
    st.dataframe(
        top_users[['event_id', 'screen_name', 'nb_tweets', 'total_retweets', 'total_replies',
                   'followers_count', 'retweet_ratio', 'engagement_score']],
        use_container_width=True
    )

    # --- Export CSV ---
    st.download_button(
        label=" Télécharger les résultats en CSV",
        data=top_users.to_csv(index=False).encode('utf-8'),
        file_name="top_influenceurs_comparaison_crises.csv",
        mime='text/csv'
    )
