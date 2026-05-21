import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from backend.services.airtable_service import AirtableService
from backend.models import BusinessCreate, BusinessCategory, Tone

airtable = AirtableService()

st.title("🏢 Isletme Yonetimi")

tab1, tab2 = st.tabs(["Isletme Listesi", "Yeni Isletme Ekle"])

with tab1:
    businesses = airtable.list_businesses()
    if businesses:
        for b in businesses:
            with st.expander(f"{'🟢' if b.active else '🔴'} {b.name} — {b.city} {b.district or ''}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text(f"Kategori: {b.category.value if hasattr(b.category, 'value') else b.category}")
                    st.text(f"Sehir: {b.city}")
                    st.text(f"Semt: {b.district}")
                    st.text(f"Ton: {b.tone.value if hasattr(b.tone, 'value') else b.tone}")
                with col2:
                    st.text(f"Dil: {b.language}")
                    st.text(f"Aktif: {'Evet' if b.active else 'Hayir'}")
                st.text(f"Anahtar Kelimeler: {b.keywords or '-'}")
                st.text(f"Ozel Prompt: {b.custom_prompt or '-'}")
                st.text(f"Adres: {b.address or '-'}")
    else:
        st.info("Henuz isletme eklenmedi.")

with tab2:
    st.subheader("➕ Yeni Isletme Ekle")
    with st.form("new_business_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Isletme Adi*", placeholder="Ornek Kebap Salonu")
            category = st.selectbox("Kategori", [c.value for c in BusinessCategory])
            city = st.text_input("Sehir*", placeholder="Gebze")
            district = st.text_input("Semt/Ilce", placeholder="Merkez")
        with col2:
            address = st.text_input("Adres", placeholder="Cumhuriyet Mah. No:10")
            tone = st.selectbox("Yanit Tonu", [t.value for t in Tone])
            language = st.selectbox("Dil", ["tr", "en", "de", "ar"])

        keywords = st.text_area("Hedef Anahtar Kelimeler", placeholder="Gebze kebap, en iyi kebap Gebze, Gebze restoran")
        custom_prompt = st.text_area(
            "Ozel Prompt (opsiyonel)",
            placeholder="Ornek: Pazar gunleri kapaliyiz, acik oldugumuzu soyleme.\nVegan menumuz var, ilgili yorumlarda belirt.\nSu anda %20 indirim kampanyamiz var.",
        )

        submitted = st.form_submit_button("Isletme Ekle")

        if submitted and name.strip() and city.strip():
            data = BusinessCreate(
                name=name.strip(),
                category=category,
                city=city.strip(),
                district=district.strip(),
                address=address.strip(),
                keywords=keywords.strip(),
                tone=tone,
                language=language,
                custom_prompt=custom_prompt.strip(),
                active=True,
            )
            airtable.create_business(data)
            st.success(f"✅ '{name}' eklendi.")
            st.rerun()
        elif submitted:
            st.error("Isletme adi ve sehir zorunludur.")
