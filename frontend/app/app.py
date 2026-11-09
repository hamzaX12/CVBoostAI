"""
CVBoost AI — Streamlit App Entry Point
Multi-page app structure with Landing Page as default entry.
"""
import os
import streamlit as st

st.set_page_config(
    page_title="CVBoost AI — Enhance your CV for better job chances",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* Remove Streamlit default header spacing globally */
header, [data-testid="stHeader"], footer, [data-testid="stBottom"], [data-testid="stToolbar"] {
    display: none !important;
    height: 0 !important;
    max-height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
.main .block-container, [data-testid="stMainBlockContainer"], div[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)

base_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(base_dir, "pages", "1_Landing.py")):
    landing_path = os.path.join(base_dir, "pages", "1_Landing.py")
    builder_path = os.path.join(base_dir, "pages", "2_Builder.py")
elif os.path.exists(os.path.join(base_dir, "app", "pages", "1_Landing.py")):
    landing_path = os.path.join(base_dir, "app", "pages", "1_Landing.py")
    builder_path = os.path.join(base_dir, "app", "pages", "2_Builder.py")
else:
    landing_path = "pages/1_Landing.py"
    builder_path = "pages/2_Builder.py"

landing = st.Page(landing_path, title="CVBoost AI — Enhance your CV for better job chances", icon="🚀", default=True, url_path="")
builder = st.Page(builder_path, title="CVBoost AI — Resume Builder", icon="📄", url_path="builder")

pg = st.navigation([landing, builder], position="hidden")

# Detect ?page=builder query param posted by landing page CTA buttons
# st.switch_page is the only way Streamlit properly updates the URL bar
if st.query_params.get("page") == "builder":
    st.query_params.clear()
    st.switch_page(builder)
elif st.query_params.get("page") == "landing":
    st.query_params.clear()
    st.switch_page(landing)

pg.run()
