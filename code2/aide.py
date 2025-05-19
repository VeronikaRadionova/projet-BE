import streamlit as st
import plotly.express as px
import pandas as pd



def getInfosAide(data):
        st.subheader("🚨 Données sur la demande d'aide")
        sensitive_stats = data.groupby('event_type')['possibly_sensitive'].mean().reset_index()
        sensitive_stats['possibly_sensitive'] *= 100
        help_counts = data.groupby(['event_type', 'is_help']).size().reset_index(name='count')
        help_counts['type'] = help_counts['is_help'].map({True: 'Aide', False: 'Autres'})

       
        help_stats = data.groupby('event_type')['is_help'].mean().reset_index(name='pourcentage_aide')
        help_stats['pourcentage_aide'] *= 100
        pourcentage = sensitive_stats['possibly_sensitive'][0]
        st.write(f"Pourcentage de tweets demandant de l'aide : {int(help_stats['pourcentage_aide'][0])}% ({help_counts['count'][1]} demande d'aides contre {help_counts['count'][0]} autres)")
        st.write(f"Pourcentage de tweets possiblement sensible :{int(pourcentage)}%")
        

def getRepartitionTypeDemande(data):
        cat_counts = data['category_name'].value_counts().reset_index()
        cat_counts.columns = ['category', 'count']
        fig3 = px.pie(cat_counts, names='category', values='count', title=f"Répartition des demandes")
        st.plotly_chart(fig3, use_container_width=True)        