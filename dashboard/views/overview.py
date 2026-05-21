import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backend.services.airtable_service import AirtableService
from dashboard.components.charts import review_trend_chart, sentiment_pie_chart

airtable = AirtableService()

st.title("📊 GMB Dashboard")

# Business filter
businesses = airtable.list_businesses()
biz_options = {"Tumu": None}
for b in businesses:
    biz_options[b.name] = b.business_id
selected_biz = st.selectbox("Isletme", options=list(biz_options.keys()), key="overview_biz")
selected_biz_id = biz_options[selected_biz]

# Summary
summary = airtable.get_summary(selected_biz_id)

# KPI Cards
cols = st.columns(6)
cols[0].metric("Toplam Yorum", summary.total_reviews)
cols[1].metric("Yanitlanan", summary.responded)
cols[2].metric("Yanit Orani", f"%{summary.response_rate}")
cols[3].metric("Ort. Puan", f"{summary.avg_rating}★")
cols[4].metric("SEO Skoru", f"%{summary.avg_seo_score}")
cols[5].metric("Bugun", f"{summary.today_reviews} yorum")

st.divider()

# Charts row
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 7 Gunluk Trend")
    chart_data = airtable.get_reviews_for_chart(business_id=selected_biz_id)
    review_trend_chart(chart_data)

with col_right:
    st.subheader("🥧 Duygu Dagilimi")
    sentiment_pie_chart(chart_data)

st.divider()

# Recent reviews table
st.subheader("📝 Son Yorumlar ve Yanitlar")
reviews = airtable.list_reviews(business_id=selected_biz_id, limit=10)

if reviews:
    rows = []
    for r in reviews:
        biz_name = next((b.name for b in businesses if b.business_id == r.business_id), "-")
        rows.append({
            "Isletme": biz_name,
            "Yorumcu": r.reviewer_name,
            "Puan": f"{r.rating}★",
            "Yorum": r.review_text[:100] + "..." if len(r.review_text) > 100 else r.review_text,
            "Yanit": (r.response_text[:100] + "..." if len(r.response_text) > 100 else r.response_text) if r.response_text else "⏳ Bekliyor",
            "Durum": r.status.value if hasattr(r.status, 'value') else r.status,
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Henuz yorum bulunmuyor.")
