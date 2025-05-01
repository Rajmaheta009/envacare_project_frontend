import os
import requests
import streamlit as st
import pandas as pd
from component.local_store import LocalStorageManager
from dotenv import load_dotenv
load_dotenv()

storage = LocalStorageManager("user_login_status")

# ✅ Initialize session state variables to prevent AttributeError
if "form_data" not in st.session_state:
    st.session_state.form_data = []
if "quotation_data" not in st.session_state:
    st.session_state.quotation_data = []
if "sample_form_data" not in st.session_state:
    st.session_state.sample_form_data = []

# API_BASE_URL
API_BASE_URL = os.getenv('API_BASE_URL')

# Page layout
col1, col2 = st.columns([5, 1])

# ✅ Dashboard Display
if st.session_state.get("login", False):
    col1.subheader(f"👋 Hello! {st.session_state.username}")
    col1.subheader(" Welcome to the Dashboard")

    # Logout button
    if col2.button("🚪 Logout"):
        st.switch_page("pages/log_out.py")
        st.rerun()

    # ✅ Customer Request Section
    st.subheader("📥 Customer Requests")
    try:
        response = requests.get(f"{API_BASE_URL}/customer_request/")

        if response.status_code == 200:
            data = response.json()

            if data:
                df = pd.DataFrame(data)
                df = df.drop(["id", "is_delete"], axis=1, errors='ignore')
                st.dataframe(df.set_index(df.columns[0]))
            else:
                st.warning("⚠️ No customer requests found")
        else:
            st.error("❌ Failed to fetch customer requests")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

    # ✅ Customer Quotations Section
    st.subheader("💰 Customer Quotations")
    try:
        response = requests.get(f"{API_BASE_URL}/quotations/")
        if response.status_code == 200:
            data = response.json()

            if data:
                df = pd.DataFrame(data)
                df = df.drop("id", axis=1, errors='ignore')
                df = df.drop("order_id", axis=1, errors='ignore')
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("⚠️ No quotations found")
        else:
            st.error("❌ Failed to fetch quotations")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

    # ✅ Sample Details Section
    st.subheader("🧪 Sample Details")
    try:
        response = requests.get(f"{API_BASE_URL}/samples/get_sample")

        if response.status_code == 200:
            data = response.json()

            if data:
                df = pd.DataFrame(data)
                df = df.drop(["id", "is_delete", "is_active", "updated_at"], axis=1, errors='ignore')
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("⚠️ No sample details found")
        else:
            st.error("❌ Failed to fetch sample details")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

else:
    st.warning("⚠️ Please login first")
    st.switch_page("main.py")
