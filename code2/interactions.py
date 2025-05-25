import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import re


def add_mentions_and_retweets_to_event(event_df, users_df, retweets_df):
    event_df['mentions'] = event_df['text'].apply(extract_mentions)  # Extraire les mentions textuelles
    user_dict = users_df.set_index('screen_name').to_dict(orient='index')  # Dictionnaire screen_name → infos utilisateur

    # Associer chaque mention à l'utilisateur correspondant dans User_clean.csv
    event_df['mentioned_users'] = event_df['mentions'].apply(lambda lst: [user_dict.get(m, {}) for m in lst])

    # Ajouter les retweeters (liens retweet → tweet original)
    event_df['retweets'] = event_df['tweet_id'].apply(
        lambda x: retweets_df[retweets_df['original_user_id'] == x]['retweeter_id'].tolist()
    )
    return event_df

# --- Crée un graphe NetworkX dirigé à partir des mentions et retweets
def create_graph(event_data, sample_size):
    # On prend un échantillon aléatoire pour éviter un graphe trop dense
    sampled = event_data.sample(n=sample_size, random_state=42) if len(event_data) > sample_size else event_data
    G = nx.DiGraph()  # Graphe orienté

    for _, row in sampled.iterrows():
        tid = row['tweet_id']  # ID du tweet

        # Ajouter les arêtes tweet → utilisateur mentionné
        for mention, user in zip(row['mentions'], row['mentioned_users']):
            if user and 'user_id' in user:
                G.add_edge(tid, user['user_id'], type='mention')

        # Ajouter les arêtes utilisateur retweeter → tweet
        for retweeter_id in row['retweets']:
            if pd.notna(retweeter_id):
                G.add_edge(retweeter_id, tid, type='retweet')

    return G

# --- Renvoie un DataFrame des utilisateurs avec le plus grand nombre d'interactions (degrés)
def get_most_active_users(G, users_df, top_n=10):
    deg = dict(G.degree())  # degré total (entrants + sortants)
    top_nodes = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # Créer un dictionnaire user_id → screen_name pour affichage
    user_map = users_df.set_index('user_id')['screen_name'].to_dict()

    results = []
    for node, interactions in top_nodes:
        if node in user_map:
            label = user_map[node]
        elif isinstance(node, int):  # tweet_id probable
            label = f"(Tweet {node})"
        else:
            label = f"(Inconnu: {node})"
        results.append((label, interactions))

    return pd.DataFrame(results, columns=["Utilisateur", "Interactions"])


# --- Affiche le graphe avec NetworkX + Matplotlib et légende personnalisée
def draw_graph(G):
    pos = nx.spring_layout(G, seed=42, k=0.2)  # disposition des nœuds
    node_sizes = [dict(G.degree())[n]*50 for n in G.nodes]  # Taille proportionnelle au degré

    plt.figure(figsize=(10, 8))

    edges = G.edges(data=True)
    edge_colors = ['violet' if e[2]['type'] == 'mention' else 'deeppink' for e in edges]  # Couleurs personnalisées

    # Dessin du graphe
    nx.draw(
        G, pos,
        with_labels=False,
        node_size=node_sizes,
        node_color="lightblue",
        edge_color=edge_colors,
        width=1.5,
        alpha=0.7,
        arrows=True
    )

    # Légende des types d’interaction
    mention_line = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='violet', label='Mentions')
    retweet_line = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='deeppink', label='Retweets')
    plt.legend(handles=[mention_line, retweet_line])
    st.pyplot(plt)

def load_data_interaction(data):
# Chargement des utilisateurs et des relations de retweets
    
    users = data["User_clean"]
    retweets = data["retweets_clean"]
    
    # Chargement des tweets pour chaque type de crise
    events = {
        'bombing': data["tweets_bombing"],
        'earthquake': data["tweets_earthquake"],
        'wildfire': data["tweets_wildfire"],
        'flood': data["tweets_flood"],
        'typhoon': data["tweets_typhoon"],
        'shooting': data["tweets_shooting"]
    }

    # Enrichissement des données pour chaque type de crise
    enriched = {}
    for name, df in events.items():
        enriched[name] = add_mentions_and_retweets_to_event(df, users, retweets)

    return enriched

def extract_mentions(text):
    return re.findall(r'@(\w+)', str(text))