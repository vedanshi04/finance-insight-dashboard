import streamlit as st
import pandas as pd
from src.preprocess import preprocess
from src.auth import auth_guard

st.set_page_config(page_title="Overview of Finance Analyzer & Visualiser", layout="wide")

auth_guard()

st.title(f"🔸Upload File to Clean")
st.markdown("---")
 
 
# File uploader that takes csv/xlsx as input 
uploaded_file = st.file_uploader(
    " Upload a .csv or .xlsx file here:",
    type=["csv", "xlsx"],
    accept_multiple_files=False
)

# Call preprocess function and store returned values
if uploaded_file:
    try:
        raw_df, clean_df, column_types, logs = preprocess(uploaded_file)

        # Save everything in session state
        st.session_state["uploaded_file"] = uploaded_file  # ✅ Needed for reprocessing
        st.session_state["raw_df"] = raw_df
        st.session_state["clean_df"] = clean_df
        st.session_state["column_types"] = column_types
        st.session_state["logs"] = logs  # ✅ Needed for log display

        st.success("✅ File processed successfully!")

    except Exception as e:
        st.error(f"❌ Error: {e}")

st.markdown("---")


# Links between pages
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(" Back to Home"):
        st.switch_page("Home.py")

with col2:
    if st.button(" Go to Data Analysis"):
        st.switch_page("pages/2_Data_Analysis.py")

with col3:
    if st.button(" Go to Data Visualization"):
        st.switch_page("pages/3_Data_Visualization.py")

with col4:
    if st.button(" Go to OpenAI Summary"):
        st.switch_page("pages/4_OpenAI_Summary.py")
        