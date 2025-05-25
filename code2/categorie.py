import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_repartition_categories_crise(df, crise, readable_topics=None):
   
    # ---  Répartition des catégories de posts ---
    st.subheader("📚 Répartition des catégories de posts")

    # Filtrer sur la crise sélectionnée
    df_filtered = df[df['topic'] == crise].copy()

    # Assurer que 'post_category' est bien une liste et exploser
    df_filtered['post_category'] = df_filtered['post_category'].apply(
        lambda x: eval(x) if isinstance(x, str) and x not in ["", "nan", "None"] else x
    )
    df_exploded = df_filtered.explode('post_category')

    # Supprimer les valeurs nulles ou vides après explosion
    df_exploded = df_exploded.dropna(subset=['post_category'])
    df_exploded = df_exploded[df_exploded['post_category'].astype(str).str.strip() != ""]

    # Groupby sur topic et post_category (même si une seule crise, pour cohérence)
    category_counts = df_exploded.groupby(["topic", "post_category"]).size().reset_index(name="count")
    if readable_topics:
        category_counts["topic"] = category_counts["topic"].map(readable_topics)

    if category_counts.empty:
        st.info("Aucune catégorie trouvée pour cette crise.")
        return

    fig_category = px.bar(
        category_counts,
        x="post_category",
        y="count",
        color="topic",
        barmode="group",
        text_auto=True,
        title="Répartition des types de posts pour la crise sélectionnée",
        labels={"post_category": "Catégorie de Post", "count": "Nombre de Tweets"}
    )
    fig_category.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig_category, use_container_width=True)

def afficher_comparaison_categories_crises(df, readable_topics=None):
  
    st.subheader("📚 Répartition des catégories de posts (Comparaison entre crises)")

    # Assurer que 'post_category' est bien une liste et exploser
    df['post_category'] = df['post_category'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    df_exploded = df.explode('post_category')

    # Supprimer les valeurs nulles après explosion
    df_exploded = df_exploded.dropna(subset=['post_category'])

    category_counts = df_exploded.groupby(["topic", "post_category"]).size().reset_index(name="count")
    if readable_topics:
        category_counts["topic"] = category_counts["topic"].map(readable_topics)

    if category_counts.empty:
        st.info("Aucune catégorie trouvée pour la comparaison.")
        return

    fig_category = px.bar(
        category_counts,
        x="post_category",
        y="count",
        color="topic",
        barmode="group",
        text_auto=True,
        title="Comparaison des types de posts entre crises",
        labels={"post_category": "Catégorie de Post", "count": "Nombre de Tweets"}
    )
    fig_category.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig_category, use_container_width=True)

