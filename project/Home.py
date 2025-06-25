import streamlit as st
from src.auth import auth_guard

auth_guard()
# PAGE CONFIG
st.set_page_config(page_title="Finance Visualizer & Summarizer", layout="wide")

# MAIN PAGE
st.title("📊 Visual & Summarizing Finance App")
st.subheader("Navigate using the sidebar or click below:")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📁 Go to File Upload (Overview)"):
        st.switch_page("pages/1_Overview.py")

with col2:
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

