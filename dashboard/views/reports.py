import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from collections import Counter
from backend.services.airtable_service import AirtableService
from dashboard.components.charts import (
    sentiment_trend_chart, seo_trend_chart, business_comparison_chart,
    keyword_bar_chart, rating_distribution_chart,
)

airtable = AirtableService()

st.title("📈 Detayli Rapor")

businesses = airtable.list_businesses()
biz_options = {"Tumu": None} | {b.name: b.business_id for b in businesses}
selected_biz = st.selectbox("Isletme", list(biz_options.keys()), key="report_biz")
selected_biz_id = biz_options[selected_biz]

tab1, tab2, tab3, tab4 = st.tabs(["Trendler", "SEO-GEO", "Karsilastirma", "Kelime Analizi"])

# ── Trendler ────────────────────────────────────────────────
with tab1:
    st.subheader("Duygu Analizi Trendi")
    chart_data = airtable.get_reviews_for_chart(business_id=selected_biz_id)
    if chart_data:
        sentiment_trend_chart(chart_data)
    else:
        st.info("Henuz yeterli veri yok.")

    st.divider()

    st.subheader("Puan Dagilimi")
    if chart_data:
        rating_distribution_chart(chart_data)

    st.divider()

    st.subheader("Yorum Yogunlugu")
    if chart_data:
        df = pd.DataFrame(chart_data)
        if not df.empty:
            df["date"] = pd.to_datetime(df["created_at"]).dt.date
            daily = df.groupby("date").size().reset_index(name="count")
            st.bar_chart(daily.set_index("date"), use_container_width=True)

# ── SEO-GEO ──────────────────────────────────────────────────
with tab2:
    st.subheader("SEO-GEO Performansi")
    seo_data = airtable.get_logs_for_seo_chart(business_id=selected_biz_id)
    if seo_data:
        seo_trend_chart(seo_data)

        # SEO stats
        scores = [d["seo_score"] for d in seo_data if d["seo_score"] > 0]
        mentions = sum(1 for d in seo_data if d.get("location_mentioned"))

        col1, col2, col3 = st.columns(3)
        col1.metric("Ort. SEO Skoru", f"%{round(sum(scores)/len(scores), 1)}" if scores else "-")
        col2.metric("Konum Geçme Orani", f"%{round(mentions/len(seo_data)*100, 1)}" if seo_data else "-")
        col3.metric("Toplam Log", len(seo_data))

        # Keywords used
        all_kw = []
        for d in seo_data:
            kw = d.get("keywords_used", "")
            if kw:
                all_kw.extend([k.strip() for k in kw.split(",") if k.strip()])
        if all_kw:
            kw_counter = Counter(all_kw)
            kw_df = pd.DataFrame(kw_counter.most_common(10), columns=["Anahtar Kelime", "Kullanim"])
            st.subheader("En Cok Kullanilan Anahtar Kelimeler")
            st.bar_chart(kw_df.set_index("Anahtar Kelime"), use_container_width=True)

        # Flag low SEO scores
        low_seo = [d for d in seo_data if d["seo_score"] < 50]
        if low_seo:
            st.warning(f"⚠️ {len(low_seo)} yanitin SEO skoru %50'nin altinda.")
    else:
        st.info("SEO-GEO verisi henuz yok.")

# ── Karsilastirma ───────────────────────────────────────────
with tab3:
    st.subheader("Isletme Bazinda Karsilastirma")
    if len(businesses) > 1:
        summaries = {}
        for b in businesses:
            summaries[b.name] = {
                "Yanit Orani": airtable.get_summary(b.business_id).response_rate,
                "Ort. Puan": airtable.get_summary(b.business_id).avg_rating,
                "SEO Skoru": airtable.get_summary(b.business_id).avg_seo_score,
            }
        business_comparison_chart(summaries)
    else:
        st.info("Karsilastirma icin en az 2 isletme gerekli.")

    st.divider()

    # Review-by-date trend per business
    st.subheader("Isletme Bazinda Yorum Trendi")
    all_chart = airtable.get_reviews_for_chart()
    if all_chart:
        df = pd.DataFrame(all_chart)
        if not df.empty:
            df["date"] = pd.to_datetime(df["created_at"]).dt.date
            for b in businesses:
                b_data = df[df["business_id"] == b.business_id]
                if not b_data.empty:
                    daily = b_data.groupby("date").size().reset_index(name=b.name)
                    st.bar_chart(daily.set_index("date"), use_container_width=True)

# ── Kelime Analizi ──────────────────────────────────────────
with tab4:
    st.subheader("Sik Kullanilan Kelimeler")
    reviews = airtable.list_reviews(business_id=selected_biz_id, limit=200)
    if reviews:
        all_text = " ".join(r.review_text for r in reviews)
        # Simple tokenization for Turkish
        words = [w.strip(".,!?():;\"'-").lower() for w in all_text.split()
                 if len(w.strip(".,!?():;\"'-")) > 3]
        stopwords = {"icin", "cok", "ile", "bir", "bu", "da", "de", "daha",
                     "ama", "veya", "olarak", "gibi", "kadar", "sonra", "ama", "oyle"}
        filtered = [w for w in words if w not in stopwords]
        word_counts = Counter(filtered).most_common(20)
        if word_counts:
            wc_df = pd.DataFrame(word_counts, columns=["Kelime", "Siklik"])
            keyword_bar_chart(wc_df)
    else:
        st.info("Kelime analizi icin yeterli yorum yok.")
