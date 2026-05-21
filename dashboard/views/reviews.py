import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from backend.services.airtable_service import AirtableService
from backend.modules.gmb_reviews.mock import MockGMB
from backend.modules.gmb_reviews.processor import ReviewProcessor
from backend.models import ReviewCreate, ReviewSource, ReviewStatus

airtable = AirtableService()
mock_gmb = MockGMB(airtable)
processor = ReviewProcessor()

st.title("💬 Yorum Yonetimi")

tab1, tab2 = st.tabs(["Yorum Listesi", "Manuel Yorum Ekle"])

with tab1:
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        businesses = airtable.list_businesses()
        biz_options = {"Tumu": None} | {b.name: b.business_id for b in businesses}
        selected_biz = st.selectbox("Isletme", list(biz_options.keys()), key="rev_biz")
    with col2:
        status_options = {"Tumu": None, "Pending": "Pending", "Responded": "Responded", "Failed": "Failed"}
        selected_status = st.selectbox("Durum", list(status_options.keys()), key="rev_status")
    with col3:
        refresh = st.button("🔄 Yenile")

    reviews = airtable.list_reviews(
        business_id=biz_options[selected_biz],
        status=status_options[selected_status],
        limit=50,
    )

    if reviews:
        rows = []
        for r in reviews:
            biz_name = next((b.name for b in businesses if b.business_id == r.business_id), "-")
            rows.append({
                "Isletme": biz_name,
                "Yorumcu": r.reviewer_name,
                "Puan": r.rating,
                "Yorum": r.review_text,
                "Yanit": r.response_text or "-",
                "Durum": r.status.value if hasattr(r.status, 'value') else r.status,
                "Tarih": r.created_at[:10] if r.created_at else "-",
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Toplam {len(reviews)} yorum gosteriliyor.")
    else:
        st.info("Filtrelere uygun yorum bulunamadi.")

with tab2:
    st.subheader("✍️ Manuel Yorum Ekle")

    businesses = airtable.list_businesses(active_only=True)
    if not businesses:
        st.warning("Once bir isletme ekleyin.")
    else:
        with st.form("manual_review_form"):
            biz_name = st.selectbox("Isletme", [b.name for b in businesses])
            reviewer = st.text_input("Yorumcu Adi", placeholder="Ahmet Y.")
            rating = st.slider("Puan", 1, 5, 4)
            review_text = st.text_area("Yorum Metni", placeholder="Harika bir deneyimdi...")
            submitted = st.form_submit_button("Yorumu Ekle ve Yanitla")

            if submitted and review_text.strip():
                selected_business = next(b for b in businesses if b.name == biz_name)
                review_data = ReviewCreate(
                    business_id=selected_business.business_id,
                    reviewer_name=reviewer or "Anonim",
                    rating=rating,
                    review_text=review_text.strip(),
                    source=ReviewSource.MANUAL,
                )
                with st.spinner("Yorum ekleniyor ve yanit uretiliyor..."):
                    created = airtable.create_review(review_data)
                    result = processor.process_one(created)
                    if result:
                        st.success(f"✅ Yanit uretildi (SEO Skoru: {result[1].seo_score})")
                        st.text_area("Uretilen Yanit", result[0].response_text, height=120)
                    else:
                        st.error("Yanit uretilemedi.")
                st.rerun()
