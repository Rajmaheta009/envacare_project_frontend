import os
import requests
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from pages.Customer_request import customer  # Assuming 'customer' contains relevant customer info

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL')
# API_BASE_URL = "http://localhost:8000"

# Initialize session state variables
if "login" not in st.session_state:
    st.session_state.login = False


# Search function
def filter_quotations(data, search_term):
    return [quote for quote in data if search_term.lower() in quote['customer_name'].lower()]


# Check for login
if st.session_state.login:
    # Page Layout
    col1, col2, col3 = st.columns([3, 1, 2])
    col1.subheader("Welcome to Quotation List")

    st.markdown("### 📄 Submitted Quotations")

    # Search Bar
    search_term = st.text_input("🔍 Search by Customer Name", "")

    try:
        response = requests.get(f"{API_BASE_URL}/quotations/")
        if response.status_code == 200:
            data = response.json()

            if data:
                # Apply search filter if there's a search term
                if search_term:
                    data = filter_quotations(data, search_term)

                for i, quote in enumerate(data, 1):
                    customer_name = quote.get("customer_name", customer.get("name", f"Customer {i}"))
                    with st.expander(f"🧾 Quotation {i}: {customer_name}", expanded=False):
                        # Display the form with quotation details
                        st.write(f"**Customer Name**: {customer_name}")
                        st.write(f"**Quotation ID**: {quote.get('id')}")
                        st.write(f"**Total Cost**: {quote.get('total_cost')}")
                        st.write(f"**PDF URL**: {quote.get('pdf_url')}")

                        # Add Edit and Delete buttons inside the expander
                        edit_button = st.button("✏️ Edit", key=f"edit_{i}")
                        delete_button = st.button("🗑️ Delete", key=f"delete_{i}")

                        # Edit button logic
                        if edit_button:
                            st.write("Edit form goes here...")
                            # Implement form to edit quotation

                        # Delete button logic
                        if delete_button:
                            st.popover("Are you sure you want to delete this quotation?")
                            col1 , col2 = st.columns([1,1])
                            yse = col1.button("Yes")
                            no = col2.button    ("no")
                            if yse:
                                delete_response = requests.delete(f"{API_BASE_URL}/quotations/{quote['id']}")
                                if delete_response.status_code == 204:
                                    st.success(f"Quotation {i} deleted successfully!")
                                else:
                                    st.error(f"Failed to delete Quotation {i}")
                            if no:
                                st.write("ohk! vdata is safe!")

            else:
                st.warning("⚠️ No customer requests found")
        else:
            st.error("❌ Failed to fetch customer requests")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

else:
    st.text("⚠️ Please login first.")
    st.switch_page('../auth_pages/login.py')
