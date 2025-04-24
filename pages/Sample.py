import os
import streamlit as st
import pandas as pd
import requests
from datetime import date
from dotenv import load_dotenv

# Load environment
load_dotenv()
API_BASE = os.getenv('API_BASE_URL')

# -------------------- Session State -------------------- #
if "login" not in st.session_state:
    st.session_state.login = True  # Change to False in production
if "form_open" not in st.session_state:
    st.session_state.form_open = False
if "edit_sample" not in st.session_state:
    st.session_state.edit_sample = None

# -------------------- API Functions -------------------- #

def safe_api_call(call):
    try:
        response = call()
        if response.status_code == 200:
            return response.json()
        st.error(f"❌ API Error: {response.text}")
    except Exception as e:
        st.error(f"🚨 Exception: {e}")
    return []

def get_all_samples():
    return safe_api_call(lambda: requests.get(f"{API_BASE}/samples/get_sample"))

def get_all_orders():
    return safe_api_call(lambda: requests.get(f"{API_BASE}/order/"))

def add_sample(data):
    try:
        res = requests.post(f"{API_BASE}/samples/", json=data)
        if res.status_code in [200, 201]:
            st.success("✅ Sample added successfully!")
        else:
            st.error(f"❌ Error: {res.text}")
    except Exception as e:
        st.error(f"🚨 Exception: {e}")

def update_sample(sample_id, data):
    try:
        res = requests.put(f"{API_BASE}/samples/{sample_id}", json=data)
        if res.status_code == 200:
            st.success("✏️ Sample updated successfully!")
        else:
            st.error(f"❌ Error: {res.text}")
    except Exception as e:
        st.error(f"🚨 Exception: {e}")

def delete_sample(sample_id):
    try:
        res = requests.delete(f"{API_BASE}/samples/{sample_id}")
        if res.status_code == 200:
            st.success("🗑️ Sample deleted.")
        else:
            st.error(f"❌ Error: {res.text}")
    except Exception as e:
        st.error(f"🚨 Exception: {e}")

# -------------------- UI Logic -------------------- #

if st.session_state.login:
    st.title("🧪 Sample Info Management")

    if st.button("➕ Add Sample Info"):
        st.session_state.form_open = True
        st.session_state.edit_sample = None

    if st.session_state.form_open:
        st.markdown("### ✍️ Sample Form")
        edit_data = st.session_state.edit_sample or {}

        orders = get_all_orders()
        if not orders:
            st.error("⚠️ No orders available. Please create an order first.")
        else:
            order_map = {order['order_number']: order['id'] for order in orders}

            with st.form("sample_form"):
                col1, col2 = st.columns(2)
                with col1:
                    selected_order = st.selectbox("📝 Select Order ID", list(order_map.keys()))
                    sample_type = st.text_input("Sample Type", edit_data.get("sample_type", ""))
                    collection_date = st.date_input("📅 Collection Date", pd.to_datetime(edit_data.get("collection_date", date.today())))
                    receipt_date = st.date_input("📥 Receipt Date", pd.to_datetime(edit_data.get("receipt_date", date.today())))
                    collected_by = st.text_input("👤 Collected By", edit_data.get("collected_by", ""))
                    particulars = st.text_input("📝 Particulars", edit_data.get("particulars", ""))
                with col2:
                    location = st.text_input("📍 Location", edit_data.get("location", ""))
                    quantity = st.text_input("📦 Quantity", edit_data.get("quantity", ""))
                    condition = st.selectbox("🩺 Condition", ["Good", "Average", "Bad"], index=["Good", "Average", "Bad"].index(edit_data.get("condition", "Good")))

                submit, cancel = st.columns([1, 1])
                if submit.form_submit_button("✅ Submit"):
                    data = {
                        "order_id": order_map[selected_order],  # Fallback if `customer` not in form
                        "sample_type": sample_type,
                        "collect_date": collection_date.isoformat(),
                        "receipt_date": receipt_date.isoformat(),
                        "collected_by": collected_by,
                        "particulars": particulars,
                        "location": location,
                        "quantity": quantity,
                        "condition": condition
                    }

                    if st.session_state.edit_sample:
                        update_sample(st.session_state.edit_sample["id"], data)
                    else:
                        add_sample(data)

                    st.session_state.form_open = False
                    st.session_state.edit_sample = None
                    st.rerun()

                if cancel.form_submit_button("❌ Cancel"):
                    st.session_state.form_open = False
                    st.session_state.edit_sample = None
                    st.warning("🚫 Form cancelled.")

    # -------------------- Show Records -------------------- #
    st.markdown("### 📄 Sample Records")
    samples = get_all_samples()
    if samples:
        for sample in samples:
            with st.expander(f"🔍 {sample.get('order_id', 'Unknown')} | {sample.get('collect_date')}"):
                st.write(f"📥 **Receipt Date**: {sample.get('receipt_date')}")
                st.write(f"👤 **Collected By**: {sample.get('collected_by')}")
                st.write(f"📝 **Particulars**: {sample.get('particulars')}")
                st.write(f"📍 **Location**: {sample.get('location')}")
                st.write(f"📦 **Quantity**: {sample.get('quantity')}")
                st.write(f"🩺 **Condition**: {sample.get('condition')}")

                col1, col2 = st.columns(2)
                if col1.button("✏️ Edit", key=f"edit_{sample['id']}"):
                    st.session_state.edit_sample = sample
                    st.session_state.form_open = True
                    st.rerun()
                if col2.button("🗑️ Delete", key=f"del_{sample['id']}"):
                    delete_sample(sample['id'])
                    st.rerun()
    else:
        st.info("ℹ️ No samples found.")
else:
    st.warning("⚠️ Please login first.")
    st.switch_page("../auth_pages/login.py")
