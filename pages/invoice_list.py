import os
import requests
import streamlit as st
from dotenv import load_dotenv
from collections import defaultdict

# Load .env and API
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL")

# Session login check
if "login" not in st.session_state:
    st.session_state.login = False


# Cache data with extended TTL for API fetch
@st.cache_data(show_spinner="Fetching data...", ttl=600)
def fetch_all_data():
    try:
        response = {
            "customers": requests.get(f"{API_BASE_URL}/customer_request/").json(),
            "orders": requests.get(f"{API_BASE_URL}/order/").json(),
            "quotations": requests.get(f"{API_BASE_URL}/quotations/").json(),
            "parameters": requests.get(f"{API_BASE_URL}/parameter/").json(),
            "samples": requests.get(f"{API_BASE_URL}/samples/get_sample").json(),
            "order_parameters": requests.get(f"{API_BASE_URL}/order_parameters/").json()
        }
        return response
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return {}


if st.session_state.login:
    st.title("📋 Full Order Viewer")

    # Fetch data from cache (or API if expired)
    data = fetch_all_data()
    if not data:
        st.error("Failed to load data.")
    else:
        customers = data.get("customers", [])
        orders = data.get("orders", [])
        quotations = data.get("quotations", [])
        parameters = data.get("parameters", [])
        samples = data.get("samples", [])
        order_parameters = data.get("order_parameters", [])

        # Create parameter map
        param_map = {param["id"]: {"name": param["name"], "price": param["price"]} for param in parameters}

        # Map customer, order, and sample
        cust_map = {cust["id"]: cust for cust in customers}
        order_map = {order["id"]: order for order in orders}
        sample_map = {samp["order_id"]: samp for samp in samples}

        # Group parameters by quotation_id
        # ✅ Group by order_id
        order_param_map = defaultdict(list)
        for op in order_parameters:
            order_param_map[op["quotation_id"]].append(op["parameter_id"])

        # Remove duplicate quotations (if API sends duplicates)
        unique_quotations = []
        seen_ids = set()
        for q in quotations:
            if q["id"] not in seen_ids:
                unique_quotations.append(q)
                seen_ids.add(q["id"])

        # Display each quotation
        for i, quote in enumerate(unique_quotations, 1):
            order = order_map.get(quote.get("order_id"), {})
            customer = cust_map.get(order.get("customer_id"), {})
            sample = sample_map.get(order.get("order_number"))  # Using order_number to find sample
            pdf_url = quote.get("pdf_url", "")
            selected_param_ids = order_param_map.get(quote.get("order_id"), [])
            selected_params = [
                {"name": param_map[param_id]["name"], "price": param_map[param_id]["price"]}
                for param_id in selected_param_ids if param_id in param_map
            ]

            with st.expander(f"🧾 Invoice Data {i}: {customer.get('name', 'Unknown')}"):
                st.markdown("### 👤 Customer Info")
                st.write(f"**Name**: {customer.get('name')}")
                st.write(f"**Email**: {customer.get('email')}")
                st.write(f"**Phone**: {customer.get('phone_number')}")
                st.write(f"**WhatsApp**: {customer.get('whatsapp_number')}")
                st.write(f"**Address**: {customer.get('address')}")

                st.markdown("### 📦 Order Info")
                st.write(f"**Order No**: {order.get('order_number')}")
                st.write(f"**Order Comment**: {order.get('order_req_comment')}")
                st.write(f"**Order Document**: {order.get('order_req_doc')}")

                st.markdown("### 🧪 Parameters")
                if selected_params:
                    for param in selected_params:
                        st.write(f"- {param['name']} — ₹{param['price']}")
                else:
                    st.write("No parameters found for this quotation.")

                st.markdown("### 🧾 Quotation PDF")
                if pdf_url:
                    st.markdown(f"[📄 Download Quotation PDF]({pdf_url})")

                if sample:
                    st.markdown("### 🧫 Sample Info")
                    st.write(f"**Sample Particulars**: {sample.get('particulars')}")
                    st.write(f"**Collected By**: {sample.get('collected_by')}")
                    st.write(f"**Date of Collection**: {sample.get('collect_date')}")
                    st.write(f"**Location**: {sample.get('location')}")
                else:
                    st.write("No sample found for this order.")
else:
    st.warning("⚠️ Please login first.")
