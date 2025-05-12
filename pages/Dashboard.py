import os
import requests
import streamlit as st
import pandas as pd
from component.local_store import LocalStorageManager
from dotenv import load_dotenv
load_dotenv()

storage = LocalStorageManager("user_login_status")

# Initialize session state variables
if "form_data" not in st.session_state:
    st.session_state.form_data = []
if "quotation_data" not in st.session_state:
    st.session_state.quotation_data = []
if "sample_form_data" not in st.session_state:
    st.session_state.sample_form_data = []

API_BASE_URL = os.getenv('API_BASE_URL')

col1, col2 = st.columns([5, 1])

if st.session_state.get("login", False):
    col1.subheader(f"👋 Hello! {st.session_state.username}")
    col1.subheader(" Welcome to the Dashboard")

    if col2.button("🚪 Logout"):
        st.switch_page("pages/log_out.py")
        st.rerun()

    # ✅ Customer Requests Section
    st.subheader("📥 Customer Requests")
    try:
        response = requests.get(f"{API_BASE_URL}/customer_request/")
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df = df.drop(["id", "is_delete"], axis=1, errors='ignore')

                # Exact search for customer name
                search_name = st.text_input("🔍 Search by Exact Customer Name").strip().lower()
                if search_name and "customer_name" in df.columns:
                    df = df[df["c_name"].str.lower() == search_name]

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

                if "created_at" in df.columns:
                    df["created_at"] = pd.to_datetime(df["created_at"])

                    # Date range filter
                    col_date1, col_date2 = st.columns(2)
                    start_date = col_date1.date_input("📅 Start Date", df["created_at"].min().date())
                    end_date = col_date2.date_input("📅 End Date", df["created_at"].max().date())
                    df = df[(df["created_at"].dt.date >= start_date) & (df["created_at"].dt.date <= end_date)]

                # Exact order ID search
                order_search = st.text_input("🔍 Search by Exact Order ID").strip().lower()
                if order_search and "order_id" in df.columns:
                    df = df[df["order_id"].astype(str).str.lower() == order_search]

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

                # Exact match for sample type
                sample_type = st.text_input("🔍 Search by Exact Sample Type").strip().lower()
                if sample_type and "sample_type" in df.columns:
                    df = df[df["sample_type"].str.lower() == sample_type]

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
