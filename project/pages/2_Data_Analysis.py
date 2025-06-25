import streamlit as st
import pandas as pd
from src.auth import auth_guard
from src.preprocess import preprocess

st.set_page_config(page_title="Data Analyser", layout="wide")

auth_guard()

st.title("Data Analysis")

if "clean_df" not in st.session_state or "raw_df" not in st.session_state:
    st.warning("Please upload and preprocess data on the 'Overview' page.")
    st.stop()


# Preserve or initialize outlier removal setting
if "remove_outliers" not in st.session_state:
    st.session_state["remove_outliers"] = True

remove_outliers = st.checkbox("Remove Outliers?", value=st.session_state["remove_outliers"])


# Reprocess if uploaded file is available and outlier checkbox state has changed
if "uploaded_file" in st.session_state:
    uploaded_file = st.session_state["uploaded_file"]
    
    # Ensure the stream is rewound before re-reading
    uploaded_file.seek(0)

    # Compare if outlier option has changed since last run
    if remove_outliers != st.session_state.get("remove_outliers", True):
        # Reprocess the file with updated outlier setting
        raw_df, clean_df, column_types, logs = preprocess(uploaded_file, remove_outliers=remove_outliers)

        # Update session state with new results
        st.session_state["raw_df"] = raw_df
        st.session_state["clean_df"] = clean_df
        st.session_state["column_types"] = column_types
        st.session_state["logs"] = logs
        st.session_state["remove_outliers"] = remove_outliers
        
    else:
        # Use existing cached values
        raw_df = st.session_state["raw_df"]
        clean_df = st.session_state["clean_df"]
        column_types = st.session_state["column_types"]
        logs = st.session_state.get("logs", {})
        
else:
    # Fallback if no uploaded_file exists
    raw_df = st.session_state["raw_df"]
    clean_df = st.session_state["clean_df"]
    column_types = st.session_state["column_types"]
    logs = st.session_state.get("logs", {})

# Displays datatypes of all columns
with st.expander("Detected Column Types : "):
    for col, ctype in column_types.items():
        st.write(f"**{col}** → `{ctype}`")


# Function to highlight changes in clean dataframe
def highlight_cleaned_changes(raw, cleaned):
    def style_func(val_raw, val_clean):
        if pd.isna(val_raw) and pd.isna(val_clean):
            return ""
        elif val_raw != val_clean:
            return "background-color: #ffcccc"  # light red
        return ""

    styles = pd.DataFrame("", index=cleaned.index, columns=cleaned.columns)
    for col in cleaned.columns:
        for i in cleaned.index:
            styles.loc[i, col] = style_func(raw.loc[i, col], cleaned.loc[i, col])

    return cleaned.style.apply(lambda _: styles, axis=None)


# 2 columns for raw and clean df
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Raw Data")
    st.dataframe(raw_df, use_container_width=True)

with col2:
    st.markdown("### 🧼 Cleaned Data")
    styled_clean = highlight_cleaned_changes(raw_df, clean_df)
    st.dataframe(styled_clean, use_container_width=True)


# Show preprocessing logs
st.markdown("### 🧾 Preprocessing Summary")
if logs:
    if logs.get("dropped_columns"):
        st.info(f"🗂 Dropped Columns (≥50% missing): {', '.join(logs['dropped_columns'])}")
    st.info(f"📛 Duplicates removed: {logs.get('duplicates_removed', 0)}")
    if remove_outliers:
        st.warning(f"📉 Outliers removed: {logs.get('outliers_removed', 0)}")

# Links for multiple pages
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Back to Home"):
        st.switch_page("Home.py")

with col2:
    if st.button("📁 Back to File Upload"):
        st.switch_page("pages/1_Overview.py")

with col3:
    if st.button("📈 Go to Data Visualization"):
        st.switch_page("pages/3_Data_Visualization.py")
