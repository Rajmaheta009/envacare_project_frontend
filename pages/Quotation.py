import requests
import streamlit as st
import pandas as pd

API_BASE_URL = "http://localhost:8000"

# Initialize session state variables
if "login" not in st.session_state:
    st.session_state.login = False
# Check for login
if st.session_state.login:
    # Page Layout
    col1, col2, col3 = st.columns([3, 1, 2])
    col1.subheader("Welcome to Quotation List")

    # Display Submitted Quotations
    st.markdown("### 📄 Submitted Quotations")

    try:
        response = requests.get(f"{API_BASE_URL}/quotations/")
        if response.status_code == 200:
            data = response.json()

            if data:
                df = pd.DataFrame(data)
                # df = df.drop("id", axis=1)
                # df = df.style.hide(axis="index")
                # df = df.drop("order_id", axis=1)
                # st.dataframe(df.style.hide(axis="index"))
                st.dataframe(df.set_index(df.columns[0]))
            else:
                st.warning("⚠️ No customer requests found")
        else:
            st.error("❌ Failed to fetch customer requests")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

else:
    st.text("⚠️ Please login first.")
    st.switch_page('../auth_pages/login.py')
