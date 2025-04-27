import streamlit as st
import plotly.express as px
import pandas as pd

def top_influenceurs(dataframes, labels):
    st.title("Top Influenceurs par Crise (Retweets + Réponses)")

    tweets = dataframes["Tweet_date_clean"]
    is_about = dataframes["is_about_clean"]
    posted = dataframes["posted_clean"]
    users = dataframes["User_clean"]
    reply_user = dataframes["reply_tweet_to_user"]

    # Normalisation
    for df in [tweets, is_about, posted]:
        df['tweet_id'] = df['tweet_id'].astype(str)
    users['user_id'] = users['user_id'].astype(str)
    reply_user['end_id'] = reply_user['end_id'].astype(str)

    tweets_base = tweets.merge(posted, on="tweet_id", how="left").merge(is_about, on="tweet_id", how="left")

    if 'reply_count' not in tweets_base.columns:
        tweets_base['reply_count'] = 0

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

    engagement['user_id'] = engagement['user_id'].astype(str)

    #  Compter les vraies réponses reçues avec end_id
    replies_received = reply_user['end_id'].value_counts().reset_index()
    replies_received.columns = ['user_id', 'nb_replies_received']

    #  Fusion avec engagement
    engagement = engagement.merge(replies_received, on='user_id', how='left')
    engagement['nb_replies_received'] = engagement['nb_replies_received'].fillna(0)

    #  Score final = retweets + vraies réponses reçues
    engagement['engagement_score'] = engagement['total_retweets'] + engagement['nb_replies_received']
    engagement['retweet_ratio'] = engagement['total_retweets'] / engagement['nb_tweets']

    # Fusion avec utilisateurs
    engagement = engagement.merge(users[['user_id', 'screen_name', 'followers_count']], on='user_id', how='left')

    #  Correspondance event_id -> label
    id_to_label = list(labels.values())
    engagement['event_name'] = engagement['event_id'].apply(lambda x: id_to_label[int(x)] if pd.notnull(x) and int(x) < len(id_to_label) else "inconnu")

    st.markdown("### Statistiques Générales")
    if not engagement.empty:
        total_influenceurs = engagement['user_id'].nunique()
        best_user = engagement.sort_values(by='engagement_score', ascending=False).iloc[0]
        st.metric("Nombre total d'influenceurs (toutes crises)", total_influenceurs)
        st.metric("Top influenceur sur les crises", f"{best_user['screen_name']} ({int(best_user['engagement_score'])} points)")

    st.markdown("### Filtres")
    event_list = sorted(engagement['event_name'].dropna().unique())
    selected_events = st.multiselect("Choisir une ou plusieurs crises :", event_list, default=event_list[:1])

    col1, col2, col3 = st.columns(3)
    top_n = col1.slider("Nombre de top utilisateurs :", 5, 30, 10)
    min_retweets = col2.number_input("Minimum de retweets", min_value=0, value=0)
    min_followers = col3.number_input("Minimum de followers", min_value=0, value=0)

    filtered = engagement[
        (engagement['event_name'].isin(selected_events)) &
        (engagement['total_retweets'] >= min_retweets) &
        (engagement['followers_count'] >= min_followers)
    ].copy()

    top_users = filtered.sort_values(by='engagement_score', ascending=False).head(top_n)

    st.subheader("Classement des influenceurs")
    if not top_users.empty:
        fig = px.bar(
            top_users,
            x='screen_name',
            y='engagement_score',
            text='engagement_score',
            color='event_name',
            hover_data=['nb_tweets', 'total_retweets', 'nb_replies_received', 'followers_count', 'retweet_ratio'],
            title="Score d'engagement (retweets + réponses reçues)",
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

        st.subheader("Détail des influenceurs")
        st.dataframe(
            top_users[['event_name', 'screen_name', 'nb_tweets', 'total_retweets', 'nb_replies_received',
                       'followers_count', 'retweet_ratio', 'engagement_score']],
            use_container_width=True
        )

        st.download_button(
            label="Télécharger les résultats en CSV",
            data=top_users.to_csv(index=False).encode('utf-8'),
            file_name="top_influenceurs_comparaison_crises.csv",
            mime='text/csv'
        )
