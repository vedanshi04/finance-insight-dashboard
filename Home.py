import streamlit as st
from src.auth import auth_guard

auth_guard()
# PAGE CONFIG
st.set_page_config(page_title="Finance Visualizer & Summarizer", layout="wide")

st.markdown("# 💼 Finance Insight Dashboard")
st.markdown("Effortlessly explore your financial data — no code required.")

st.markdown("---")
with st.container():
    st.markdown("""
    <div style='padding: 20px; border: 1px solid #444; border-radius: 12px; background-color: #2c3e50; color: #ecf0f1'>
    <h4>🚦 How It Works</h4>
    <ul>
        <li><b> Step 1:</b> Upload your CSV or Excel file</li>
        <li><b> Step 2:</b> Auto-clean and classify column types</li>
        <li><b> Step 3:</b> Analyze with grouping and aggregation</li>
        <li><b> Step 4:</b> Visualize trends with dynamic charts</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# Expandable section with deeper info
with st.expander("🔹 Learn more about features"):
    st.markdown("#### • Column Type Detection")
    st.markdown("- Automatically distinguishes between numeric, datetime, categorical, and free-text columns.\n- Handles mixed-type columns intelligently.")

    st.markdown("#### • Data Cleaning")
    st.markdown("- Fills missing values smartly.\n- Converts invalid values.\n- Removes duplicates and outliers (optional).")

    st.markdown("#### • Time-based Grouping")
    st.markdown("- Group your data by day, month, quarter, or year.\n- Choose from different aggregations like count, sum, or average.")

    st.markdown("#### • Visualizations")
    st.markdown("- Interactive plots automatically adapt based on the column types.\n- Includes time series, treemaps, area plots, and category heatmaps.")

    st.markdown("#### • Preprocessing Logs")
    st.markdown("- View what columns were dropped, which rows were cleaned, and how data was transformed.\n- Great for transparency and learning.")

st.info(" • Whether you're an analyst or a student — get clean, visual insights in seconds.")


col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Go to File Upload"):
        st.switch_page("pages/1_File_Upload.py")

with col2:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

