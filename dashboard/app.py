import streamlit as st

st.set_page_config(
    page_title="GMB Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Overview": [
        st.Page("views/overview.py", title="Ozet", icon="🏠"),
    ],
    "Yonetim": [
        st.Page("views/reviews.py", title="Yorumlar", icon="💬"),
        st.Page("views/businesses.py", title="Isletmeler", icon="🏢"),
    ],
    "Raporlar": [
        st.Page("views/reports.py", title="Detayli Rapor", icon="📈"),
    ],
}

pg = st.navigation(pages)
pg.run()
