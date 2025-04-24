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
st.session_state.setdefault("login", True)  # Change to False in production
st.session_state.setdefault("form_open", False)
st.session_state.setdefault("edit_sample", None)

# -------------------- API Functions -------------------- #
def safe_api_call(call, default=[]):
    try:
        response = call()
        if response.status_code == 200:
            return response.json()
        st.error(f"❌ API Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"🚨 Exception: {e}")
    return default

def get_all_samples():
    return safe_api_call(lambda: requests.get(f"{API_BASE}/samples/get_sample"))

def get_all_orders():
    return safe_api_call(lambda: requests.get(f"{API_BASE}/order/"))

def add_sample(data):
    return safe_api_call(lambda: requests.post(f"{API_BASE}/samples/", json=data))

def update_sample(sample_id, data):
    return safe_api_call(lambda: requests.put(f"{API_BASE}/samples/{sample_id}", json=data))

def delete_sample(sample_id):
    return safe_api_call(lambda: requests.delete(f"{API_BASE}/samples/{sample_id}"))

# -------------------- UI Logic -------------------- #
if not st.session_state.login:
    st.warning("⚠️ Please login first.")
    st.switch_page("../auth_pages/login.py")

st.title("🧪 Sample Info Management")

# Load orders upfront
orders = get_all_orders()
order_map = {order['order_number']: order['order_number'] for order in orders}

# Add Sample Form (Global - Optional)
if st.button("➕ Add Sample Info"):
    st.session_state.form_open = "new"
    st.session_state.edit_sample = None

if st.session_state.form_open == "new":
    st.markdown("### ✍️ Add New Sample")
    with st.form("new_sample_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_order = st.selectbox("📝 Select Order ID", list(order_map.keys()))
            sample_type = st.text_input("Sample Type", "")
            collection_date = st.date_input("📅 Collection Date", date.today())
            receipt_date = st.date_input("📥 Receipt Date", date.today())
            collected_by = st.text_input("👤 Collected By", "")
            particulars = st.text_input("📝 Particulars", "")
        with col2:
            location = st.text_input("📍 Location", "")
            quantity = st.number_input("📦 Quantity", value=1.0, min_value=1.0)
            condition = st.selectbox("🩺 Condition", ["Good", "Average", "Bad"])

        submit, cancel = st.columns([1, 1])
        if submit.form_submit_button("✅ Submit"):
            data = {
                "order_id": str(order_map[selected_order]),
                "sample_type": sample_type,
                "collect_date": collection_date.isoformat(),
                "receipt_date": receipt_date.isoformat(),
                "collected_by": collected_by,
                "particulars": particulars,
                "location": location,
                "quantity": quantity,
                "condition": condition
            }
            add_sample(data)
            st.success("✅ Sample added successfully!")
            st.session_state.form_open = False
            st.rerun()

        if cancel.form_submit_button("❌ Cancel"):
            st.session_state.form_open = False
            st.warning("🚫 Add form cancelled.")

# -------------------- Show Records -------------------- #
st.markdown("### 📄 Sample Records")
samples = get_all_samples()
if samples:
    for sample in samples:
        with st.expander(f"🔍 Order ID: {sample.get('order_id', 'Unknown')} | Date: {sample.get('collect_date')}"):
            st.write(f"📥 **Receipt Date**: {sample.get('receipt_date')}")
            st.write(f"👤 **Collected By**: {sample.get('collected_by')}")
            st.write(f"📝 **Particulars**: {sample.get('particulars')}")
            st.write(f"📍 **Location**: {sample.get('location')}")
            st.write(f"📦 **Quantity**: {sample.get('quantity')}")
            st.write(f"🩺 **Condition**: {sample.get('condition')}")

            col1, col2 = st.columns(2)
            if col1.button("✏️ Edit", key=f"edit_{sample['id']}"):
                st.session_state.edit_sample = sample
                st.session_state.form_open = sample['id']
                st.rerun()

            if col2.button("🗑️ Delete", key=f"delete_{sample['id']}"):
                delete_sample(sample['id'])
                st.rerun()

            if st.session_state.form_open == sample["id"]:
                st.markdown("#### ✍️ Edit Sample")
                with st.form(f"edit_form_{sample['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_order = st.selectbox("📝 Select Order ID", list(order_map.keys()))
                        sample_type = st.text_input("Sample Type", sample.get("sample_type", ""))
                        collection_date = st.date_input("📅 Collection Date", pd.to_datetime(sample.get("collect_date", date.today())))
                        receipt_date = st.date_input("📥 Receipt Date", pd.to_datetime(sample.get("receipt_date", date.today())))
                        collected_by = st.text_input("👤 Collected By", sample.get("collected_by", ""))
                        particulars = st.text_input("📝 Particulars", sample.get("particulars", ""))
                    with col2:
                        location = st.text_input("📍 Location", sample.get("location", ""))
                        quantity = st.number_input("📦 Quantity", value=sample.get("quantity", 1.0), min_value=1.0)
                        condition = st.selectbox("🩺 Condition", ["Good", "Average", "Bad"], index=["Good", "Average", "Bad"].index(sample.get("condition", "Good")))

                    submit, cancel = st.columns([1, 1])
                    if submit.form_submit_button("✅ Update"):
                        data = {
                            "order_id": str(order_map[selected_order]),
                            "sample_type": sample_type,
                            "collect_date": collection_date.isoformat(),
                            "receipt_date": receipt_date.isoformat(),
                            "collected_by": collected_by,
                            "particulars": particulars,
                            "location": location,
                            "quantity": quantity,
                            "condition": condition
                        }
                        update_sample(sample['id'], data)
                        st.success("✏️ Sample updated successfully!")
                        st.session_state.form_open = False
                        st.session_state.edit_sample = None
                        st.rerun()

                    if cancel.form_submit_button("❌ Cancel"):
                        st.session_state.form_open = False
                        st.session_state.edit_sample = None
                        st.warning("🚫 Edit cancelled.")
else:
    st.info("ℹ️ No samples found.")
