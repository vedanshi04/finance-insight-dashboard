import streamlit as st

def auth_guard():
    # Only initialize once
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Hide sidebar using CSS
        st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    visibility: hidden;
                    width: 0px;
                }
                [data-testid="collapsedControl"] {
                    display: none;
                }
            </style>
        """, unsafe_allow_html=True)


        # Show login form
        st.title("🔐 Login Required")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "admin" and password == "1234":
                st.session_state.authenticated = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

        st.stop()  # Prevent rest of the app from running
