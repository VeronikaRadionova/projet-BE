import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def repartitionSentiment(df_crisis):
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
