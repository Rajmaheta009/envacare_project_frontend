import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')

# Initialize session state
if "login" not in st.session_state:
    st.session_state.login = False

# Search filter
def filter_quotations(data, search_term):
    return [quote for quote in data if search_term.lower() in quote['customer_name'].lower()]

# ✅ Multi-API Call Function
def get_complete_quotation_data():
    try:
        quotations_res = requests.get(f"{API_BASE_URL}/quotations/")
        if quotations_res.status_code != 200:
            st.error("Failed to fetch quotations.")
            return []

        quotations = quotations_res.json()
        combined_data = []

        for quote in quotations:
            quote_id = quote.get("id")
            order_id = quote.get("order_id")
            pdf_url = quote.get("pdf_url")

            # Fetch Order
            order = {}
            customer = {}
            parameters = []

            if order_id:
                order_res = requests.get(f"{API_BASE_URL}/order/order_id/{order_id}")
                if order_res.status_code == 200:
                    order = order_res.json()
                    customer_id = order.get("customer_id")

                    # Fetch Customer
                    if customer_id:
                        cust_res = requests.get(f"{API_BASE_URL}/customer_request/{customer_id}")
                        if cust_res.status_code == 200:
                            customer = cust_res.json()

            # Fetch Parameters
            param_res = requests.get(f"{API_BASE_URL}/order_parameters/op_id/{quote_id}")
            if param_res.status_code == 200:
                para = param_res.json()
                for item in para:
                    p_id = item["parameter_id"]
                    if p_id :
                        p_res= requests.get(f"{API_BASE_URL}/parameter/p_id/{p_id}")
                        if p_res.status_code == 200:
                            param_data = p_res.json()
                            # If it's a list, extend; if it's a dict, append
                            if isinstance(param_data, list):
                                parameters.extend(param_data)
                            elif isinstance(param_data, dict):
                                parameters.append(param_data)

            combined_data.append({
                "id": quote_id,
                "pdf_url": pdf_url,
                "parameters": parameters,
                "customer_name": customer.get("name", "Unknown"),
                "customer_email": customer.get("email", ""),
                "order_number": order.get("order_number", "")
            })

        return combined_data

    except Exception as e:
        st.error(f"Error fetching quotation data: {e}")
        return []

# Main App
if st.session_state.login:
    col1, col2, col3 = st.columns([3, 1, 2])
    col1.subheader("Welcome to Quotation List")
    st.markdown("### 📄 Submitted Quotations")

    search_term = st.text_input("🔍 Search by Customer Name", "")
    data = get_complete_quotation_data()

    if data:
        if search_term:
            data = filter_quotations(data, search_term)

        for i, quote in enumerate(data, 1):
            with st.expander(f"🧾 Quotation {i}: {quote['customer_name']}", expanded=False):
                st.write(f"**Customer Name**: {quote['customer_name']}")
                st.write(f"**Customer Email**: {quote['customer_email']}")
                st.write(f"**Order Number**: {quote['order_number']}")
                st.write(f"[📄 Download PDF]({quote['pdf_url']})")

                st.markdown("**🧪 Parameters Selected:**")
                for param in quote['parameters']:
                    st.write(f"- {param['name']} — ₹{param['price']}")

                edit_button = st.button("✏️ Edit", key=f"edit_{i}")
                delete_button = st.button("🗑️ Delete", key=f"delete_{i}")

                if edit_button:
                    st.info("Edit form goes here... (To be implemented)")

                if delete_button:
                    with st.popover("Are you sure you want to delete this quotation?"):
                        c1, c2 = st.columns([1, 1])
                        if c1.button("Yes", key=f"yes_{i}"):
                            del_res = requests.delete(f"{API_BASE_URL}/quotations/{quote['id']}")
                            if del_res.status_code == 204:
                                st.success(f"Quotation {i} deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete Quotation {i}")
                        if c2.button("No", key=f"no_{i}"):
                            st.write("Action cancelled.")

    else:
        st.warning("⚠️ No quotations found.")

else:
    st.warning("⚠️ Please login first.")
    st.switch_page('../auth_pages/login.py')