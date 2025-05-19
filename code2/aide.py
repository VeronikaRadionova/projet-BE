import streamlit as st
import plotly.express as px
import pandas as pd


def proportionAideTweet(data):
        st.subheader("🆘 Proportion de tweets d'aide par crise")
        help_stats = data.groupby('event_type')['is_help'].mean().reset_index(name='pourcentage_aide')
        help_stats['pourcentage_aide'] *= 100

        fig2 = px.bar(help_stats, x="event_type", y="pourcentage_aide",
                      labels={"event_type": "Type de crise", "pourcentage_aide": "% Aide"},
                      title="Part des tweets d'aide par type de crise")
        fig2.update_traces(texttemplate='%{y:.1f}%', textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)
