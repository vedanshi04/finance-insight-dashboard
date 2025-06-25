import streamlit as st
import openai
from openai import OpenAIError

st.set_page_config(page_title="Summary", page_icon="📝")
st.title("📝 Data Summarization")

# Safely load API key
if "openai" in st.secrets:
    openai.api_key = st.secrets["openai"]["api_key"]
else:
    st.error("🔐 OpenAI API key not found in secrets. Please add it to .streamlit/secrets.toml.")
    st.stop()

    
# Check for clean_df in session state
if "clean_df" not in st.session_state:
    st.warning("⚠️ Please upload and preprocess a file first in the 'File Upload' page.")
    if st.button("Go to File Upload"):
        st.switch_page("pages/1_File_Upload.py")
    st.stop()

df = st.session_state["clean_df"]
st.markdown("---")

st.subheader("🔸Preview of Cleaned Data")
st.dataframe(df.head(10), use_container_width=True)

st.markdown("---")

if st.button("🔸 Generate Summary"):
    try:
        

        # Convert small sample of data to string
        sample_text = df.head(100).to_csv(index=False)

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": f"Summarize the following data:\n{sample_text}"}
            ],
            temperature=0.3
        )

        summary = response.choices[0].message.content
        st.subheader("📋 Summary")
        st.write(summary)

    except OpenAIError as e:
        st.error("OpenAI API : This feature requires a premium account or a valid API key.")
      

st.markdown("---")

# Navigation
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("Back to Home"):
        st.switch_page("Home.py")
with col2:
    if st.button("Back to File Upload "):
        st.switch_page("pages/1_File_Upload.py")
with col3:
    if st.button("Back to Data Analysis"):
        st.switch_page("pages/2_Data_Analysis.py")        
with col4:
    if st.button(" Go to OpenAI Summary"):
        st.switch_page("pages/4_OpenAI_Summary.py")
with col5:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.switch_page("Home.py")
