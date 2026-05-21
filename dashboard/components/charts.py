import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter


def review_trend_chart(data: list[dict]):
    if not data:
        st.info("Veri yok.")
        return
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    daily = df.groupby("date").agg(
        yorum=("status", "count"),
        yanitlanan=("status", lambda x: (x == "Responded").sum()),
    ).reset_index()
    fig = px.line(daily, x="date", y=["yorum", "yanitlanan"],
                  labels={"value": "Adet", "date": "Tarih", "variable": "Tip"},
                  color_discrete_map={"yorum": "#1f77b4", "yanitlanan": "#2ca02c"})
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
    st.plotly_chart(fig, use_container_width=True)


def sentiment_pie_chart(data: list[dict]):
    if not data:
        st.info("Veri yok.")
        return
    sentiments = [d.get("sentiment", "Notr") for d in data]
    counts = Counter(sentiments)
    fig = px.pie(names=list(counts.keys()), values=list(counts.values()),
                 color_discrete_map={"Pozitif": "#2ca02c", "Negatif": "#d62728", "Notr": "#7f7f7f"})
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
    st.plotly_chart(fig, use_container_width=True)


def sentiment_trend_chart(data: list[dict]):
    if not data:
        st.info("Veri yok.")
        return
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    daily = df.groupby(["date", "sentiment"]).size().reset_index(name="count")
    fig = px.line(daily, x="date", y="count", color="sentiment",
                  color_discrete_map={"Pozitif": "#2ca02c", "Negatif": "#d62728", "Notr": "#7f7f7f"},
                  labels={"count": "Adet", "date": "Tarih", "sentiment": "Duygu"})
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)


def seo_trend_chart(data: list[dict]):
    if not data:
        st.info("SEO verisi yok.")
        return
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    daily = df.groupby("date")["seo_score"].mean().reset_index()
    daily["seo_score"] = daily["seo_score"].round(1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["seo_score"],
                             mode="lines+markers", name="SEO Skoru",
                             line=dict(color="#9467bd", width=2)))
    fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Hedef: 70")
    fig.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Esik: 50")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350,
                      yaxis_range=[0, 100], yaxis_title="SEO Skoru (%)")
    st.plotly_chart(fig, use_container_width=True)


def business_comparison_chart(data: dict[str, dict]):
    names = list(data.keys())
    response_rates = [data[n]["Yanit Orani"] for n in names]
    avg_ratings = [data[n]["Ort. Puan"] for n in names]
    seo_scores = [data[n]["SEO Skoru"] for n in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Yanit Orani (%)", x=names, y=response_rates, marker_color="#1f77b4"))
    fig.add_trace(go.Bar(name="Ort. Puan", x=names, y=avg_ratings, marker_color="#ff7f0e"))
    fig.add_trace(go.Bar(name="SEO Skoru (%)", x=names, y=seo_scores, marker_color="#9467bd"))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350, barmode="group")
    st.plotly_chart(fig, use_container_width=True)


def keyword_bar_chart(data: pd.DataFrame):
    if data.empty:
        st.info("Veri yok.")
        return
    fig = px.bar(data.head(15), x="Kelime", y="Siklik", color="Siklik",
                 color_continuous_scale="Blues")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)


def rating_distribution_chart(data: list[dict]):
    if not data:
        st.info("Veri yok.")
        return
    ratings = [d.get("rating", 0) for d in data]
    counts = Counter(ratings)
    labels = [f"{r} Yildiz" for r in sorted(counts.keys())]
    values = [counts[r] for r in sorted(counts.keys())]
    colors = ["#d62728", "#ff7f0e", "#ffdd57", "#7ec8a1", "#2ca02c"]
    fig = px.bar(x=labels, y=values, color=labels, color_discrete_sequence=colors)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300,
                      xaxis_title="Puan", yaxis_title="Adet")
    st.plotly_chart(fig, use_container_width=True)
