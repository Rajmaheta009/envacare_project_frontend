import base64
import os
from datetime import datetime

import pandas as pd
import streamlit as st
import requests
from streamlit import session_state
from pdf_converter_files.qoutation_invoice_maker import main
from pages.parameter import fetch_parameters
from dotenv import load_dotenv
load_dotenv()


current_date = datetime.now()

# API URLs
# API_BASE_URL = "http://localhost:8000"
API_BASE_URL = os.getenv('API_BASE_URL')
CUSTOMER_API = f"{API_BASE_URL}/customer_request/"
ORDER_API = f"{API_BASE_URL}/order/"
QUOTATION_API = f"{API_BASE_URL}/quotations/"
ORDER_PARAMETER = f"{API_BASE_URL}/order_parameters/"

## Fetch all parameters
parameters = fetch_parameters()
# st.write(parameters)

# Prepare filtered list and child map
filtered_params = []
child_map = {}

for param in parameters:
    price = param.get("price")
    if price is None:
        continue  # Skip parameters without a price

    name = param.get("name", "Unnamed")
    parent_name = param.get("parent_name")
    child_name = param.get("child_name")
    parent_id = param.get("parent_id")

    # Build display title
    if parent_name and child_name:
        title = f"{parent_name} > {child_name}"
    elif parent_name:
        title = f"{parent_name} - {name}"
    else:
        title = name

    # Add to filtered list
    filtered_params.append({
        "id": param["id"],
        "title": title,
        "name": param["name"],
        "price": param["price"],  # ← Consistent field name
        "parent_id": param.get("parent_id")
    })

    # Map children to parent ID
    if parent_id:
        child_map.setdefault(parent_id, []).append(param)


# Initialize session state variables
if "show_form" not in st.session_state:
    st.session_state.show_form = False
if "selected_customer_id" not in st.session_state:
    st.session_state.selected_customer_id = None
if "customer_to_edit" not in st.session_state:
    st.session_state.customer_to_edit = None
if "selected_parameters" not in st.session_state:
    st.session_state.selected_parameters = {}
if "filter_mode" not in st.session_state:
    st.session_state.filter_mode = False
if "search_term" not in st.session_state:
    st.session_state.search_term = ""


# @st.cache_data(show_spinner="Fetching data...", ttl=600)
def fetch_customers_with_orders():
    try:
        customer_response = requests.get(CUSTOMER_API)
        order_response = requests.get(ORDER_API)

        if customer_response.status_code != 200:
            st.error(f"Customer API error: {customer_response.status_code}")
            return []

        if order_response.status_code != 200:
            st.error(f"Order API error: {order_response.status_code}")
            return []

        customers = customer_response.json()
        orders = order_response.json()

        order_map = {order['customer_id']: order for order in orders}
        for customer in customers:
            customer_id = customer.get("id")
            order = order_map.get(customer_id, {})
            customer["o_number"] = order.get("order_number", "No Order Number")
            customer["order_req_comment"] = order.get("order_req_comment", "No comment")
            customer["order_req_doc"] = order.get("order_req_doc", "No document")

        return customers
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        return []

# ✅ Function to fetch customer details by ID
def fetch_customer_by_id(customer_id):
    try:
        customer = requests.get(f"{CUSTOMER_API}{customer_id}").json()
        return customer
    except Exception as e:
        st.error(f"⚠️ Error fetching customer details: {e}")
        return None

# ✅ Function to fetch order details by customer ID
def fetch_order_by_customer_id(customer_id):
    try:
        order = requests.get(f"{ORDER_API}c_id/{customer_id}").json()
        return order
    except Exception as e:
        st.error(f"⚠️ Error fetching order details: {e}")
        return None


# ✅ Function to create customer and order
def create_customer_and_order(data, comment, docfile):
    try:
        response = requests.post(CUSTOMER_API, json=data)
        if response.status_code == 200:
            customer = response.json()
            customer_id = customer.get("id")
            customer_name = customer.get("name")
            formatted_date = current_date.strftime("%m**%d/")
            order_data = {
                "customer_id": customer_id,
                "order_req_comment": comment,
                "status": "Quotation Check",
                "order_number" : f"{customer_name}/{formatted_date}/ORDERNo{customer_id}"
            }
            files = {'docfile': docfile} if docfile else None
            order_response = requests.post(ORDER_API, data=order_data, files=files)
            if order_response.status_code == 200:
                st.success("✅ Customer and Order created successfully!")
                st.session_state.show_form = False
                st.rerun()
            else:
                st.error(f"❌ Failed to create order. Status: {order_response.status_code}")
        else:
            st.error(f"❌ Failed to create order. Status: {response.status_code}")
            st.error(f"❌ Failed to create order. Status: {response.json()}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# ✅ Function to update customer and order
def update_customer_and_order(customer_id, order_id, data, comment, docfile):
    try:
        response = requests.put(f'{CUSTOMER_API}{customer_id}', json=data)
        if response.status_code == 200:
            order_data = {
                "customer_id": customer_id,
                "order_req_comment": comment,
                "status": "Quotation Check"
            }
            if st.session_state.doc_check != docfile:
                files = {'docfile': docfile}
                order_response = requests.put(f"{ORDER_API}{order_id}", data=order_data, files=files)
            else:
                order_response = requests.put(f"{ORDER_API}{order_id}", data=order_data)

            if order_response.status_code == 200:
                st.success("✅ Customer and Order updated successfully!")
                st.session_state.show_form = False
                st.rerun()
            else:
                st.error(f"❌ Failed to update order. Status: {order_response.status_code}")
                st.write(order_data)
                st.write(files)
                st.write(order_id)
                # st.write(session_state.c_id)


    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# ✅ Function to delete customer and order
def delete_customer_with_order(c_id, o_id):
    delete_c = requests.delete(f"{CUSTOMER_API}{c_id}")
    if delete_c.status_code == 204:
        delete_o = requests.delete(f"{ORDER_API}{o_id}")
        if delete_o.status_code == 200:
            st.success("Deleted Successfully")
        else:
            st.error("❌ Failed to delete Order.")
    else:
        st.error("❌ Failed to delete Customer Request.")

# ✅ Updated function to include quantity and safe deselection
def render_parameters(parent_id=None, level=0):
    children = [p for p in parameters if p.get("parent_id") == parent_id]

    for p in children:
        param_id = p["id"]
        name = p["name"]
        price = p.get("price")
        key = f"{param_id}_{name}"
        qty_key = f"qty_{param_id}"
        indent = " " * level  # use em-space for better spacing (visual indent)

        if price is not None:
            checked = st.checkbox(f"{indent}{name} ₹{price}", key=key)

            if checked:
                qty = st.number_input(f"{indent}Enter Quantity for {name}", min_value=1, step=1, key=qty_key)
                total_cost = int(price) * int(qty)
                st.markdown(f"**{indent}Total: ₹{price} × {qty} = ₹{total_cost}**")

                st.session_state.selected_parameters[param_id] = {
                    "name": name,
                    "cost": int(price),
                    "quantity": int(qty),
                    "total": total_cost
                }
            else:
                st.session_state.selected_parameters.pop(param_id, None)
        else:
            st.markdown(f"**{indent}{name}**")  # just label

        # 🔁 Recurse for children
        render_parameters(parent_id=param_id, level=level + 1)

# ✅ Updated: render_filtered_parameters() Function
def render_filtered_parameters():
    for p in parameters:
        price = p.get("price")
        if price is None or st.session_state.search_term not in p["name"].lower():
            continue  # Skip if no price or doesn't match search

        key = f"{p['id']}_{p['name']}"
        qty_key = f"qty_{p['id']}"
        checked = st.checkbox(f"{p['name']} ₹{price}", key=key)

        if checked:
            qty = st.number_input(f"Qty for {p['name']}", min_value=1, step=1, key=qty_key)
            st.session_state.selected_parameters[p["id"]] = {
                "name": p["name"],
                "cost": int(price),
                "quantity": int(qty),
                "total": int(price) * int(qty)
            }
        else:
            st.session_state.selected_parameters.pop(p["id"], None)

# ✅ Create Quotation with Static File Upload
def create_quotation(customer_id,order_id, selected_param_data):
    try:
        payload = {
            "customer_id": customer_id,
            "order_id": order_id,
            "parameter_info": selected_param_data
        }

        response = requests.post(QUOTATION_API, json=payload)

        if response.status_code == 200:
            all_info = response.json()
            q_id = all_info.get('quotation_id')
            return q_id
        else:
            st.error("❌ Failed to create quotation")
            st.write(response.text)
            st.write(payload)
            return None
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        return None



def save_selected_parameters_to_api(quotation_id):
    selected = st.session_state.get("selected_parameters", {})
    for param_id, cost in selected.items():
        payload = {
            "quotation_id": quotation_id,
            "parameter_id": param_id,
            "cost": cost["cost"],
            "result": "None",
            "is_delete": False,
            "is_active": True
        }
        response = requests.post(ORDER_PARAMETER, json=payload)
        if response.status_code != 200:
            st.error(f"❌ Failed to save parameter {param_id}")
            st.write(payload)
    st.success(f"✅ Parameter saved")


# ✅ Main App Logic
if session_state.login:
    st.title("📝 Customer Requests")

    if st.button("➕ Add Request"):
        st.session_state.show_form = True

    if st.session_state.show_form:
        with st.form("customer_form"):
            st.markdown("### 🛠️ Add New Customer Request")

            c_name = st.text_input("Company Name",placeholder="Enter company name",max_chars=50)
            col1, col2 = st.columns(2)
            name = col1.text_input("Person Name", placeholder="Enter person name", max_chars=50)
            email = col2.text_input("Email ID", placeholder="Enter customer email")

            col3, col4 = st.columns(2)
            phone = col3.text_input("Phone Number", placeholder="Enter phone number")
            whatsapp = col4.text_input("WhatsApp Number", placeholder="Enter WhatsApp number")

            address = st.text_area("Address", placeholder="Enter customer address")

            col5, col6 = st.columns(2)
            comment = col5.text_area("Comment", placeholder="Add comments")
            document = col6.file_uploader("Upload Document", type=["pdf", "docx", "txt", "xlsx", "csv"])

            submit_btn = st.form_submit_button("✅ Submit")
            cancel_btn = st.form_submit_button("❌ Cancel")

        if submit_btn:
            if name and email and phone and (comment or document):
                new_customer = {
                    "c_name" : c_name,
                    "name": name,
                    "email": email,
                    "phone_number": phone,
                    "whatsapp_number": whatsapp,
                    "address": address,
                    "is_delete": False
                }
                create_customer_and_order(new_customer, comment, document)
            else:
                st.error("❌ Please fill all required fields and add a comment or document.")

        if cancel_btn:
            st.session_state.show_form = False
            st.rerun()


    # 🚀 Display Customers
    st.markdown("### 📊 Submitted Customer Requests")
    customers = fetch_customers_with_orders()
    if not customers:
        st.warning("⚠️ No customer requests found")

    search = st.text_input("🔍 Search Customer by name or email", "").lower().strip()
    # Filter customers based on search input
    filtered_customers = [
        customer for customer in customers
        if search in customer['name'].lower() or search in customer['email'].lower() or search in customer['c_name'].lower()
]
    if customers:
        for customer in filtered_customers:
            customer_id = customer.get("id")
            # session_state.c_id=customer_id
            with st.expander(f"{customer['name']} - {customer['email']}"):
                st.write(f"**Order Number :** {customer['o_number']}")
                st.write(f"**Company Name :** {customer['c_name']}")
                st.write(f"**Address:** {customer['address']}")
                st.write(f"**Phone:** {customer['phone_number']}")
                st.write(f"**WhatsApp:** {customer['whatsapp_number']}")
                st.write(f"**Comment:** {customer['order_req_comment']}")
                st.write(f"**Document:** {customer['order_req_doc']}")
                # st.write(customer)

                col1, col2 = st.columns([1, 1])

                if col1.button(f"Edit => {customer['name']}", key=f"edit_{customer_id}"):
                    customer_details = fetch_customer_by_id(customer_id)
                    if customer_details:
                        st.session_state.show_form = True
                        st.session_state.customer_to_edit = customer_details

                with col2.popover(f"Delete => {customer['name']}"):
                    st.subheader("Are You Sure ?!")
                    col1, col2 = st.columns([1, 2])
                    if col1.button("YES", key=f"del_yes_{customer_id}"):
                        order = fetch_order_by_customer_id(customer_id)
                        order_id = order.get("id")
                        delete_customer_with_order(customer_id, order_id)
                    if col2.button("No", key=f"del_no_{customer_id}"):
                        st.write("Ok! Info Is Safe")

                if st.button(f"➕ Add Quotation", key=f"quote_{customer_id}"):
                    st.session_state.selected_customer_id = customer_id

                # ✅ Show Quotation form directly inside expander if selected
                if st.session_state.selected_customer_id == customer_id:
                    st.markdown("### 🧾 Add Quotation")

                    col1, col2, col3 = st.columns([2, 3, 2])
                    with col1:
                        st.subheader("Customer Info")
                        st.write(f"Name: {customer['name']}")
                        st.write(f"Email: {customer['email']}")
                        st.write(f"Phone: {customer['phone_number']}")
                        st.write(f"WhatsApp: {customer['whatsapp_number']}")
                        st.write(f"Comment: {customer['order_req_comment']}")
                        st.write(f"document: {customer['order_req_doc']}")

                    selected_parameters = {}
                    parameters = fetch_parameters()
                    # Split parent and child parameters
                    parent_parameters = [p for p in parameters if p["price"] is None]
                    # Create child mapping by parent_id
                    child_map = {}
                    for p in parameters:
                        parent_id = p.get("parent_id")
                        if parent_id is not None:
                            child_map.setdefault(parent_id, []).append(p)

                    with col2:
                        with col2:
                            st.subheader("📌 Select Parameters")
                            search_term = st.text_input("🔍 Filter by parameter name", "", ).lower().strip()
                            search_btn = st.button("Search")
                            with st.container(height=500, border=False):
                                if search_term == "":
                                    for parent in parent_parameters:
                                        if parent["parent_id"] is None:
                                            st.markdown(f"### {parent['name']}")
                                            render_parameters(parent["id"])

                                else:
                                    render_filtered_parameters()

                    with col3:
                        st.subheader("🧾 Selected Parameters")

                        selected = st.session_state.get("selected_parameters", {})
                        if selected:
                            total = 0
                            table_data = []

                            for param in selected.values():
                                name = param.get("name", "Unnamed")
                                qty = int(param.get("quantity", 0))
                                price = int(param.get("cost", 0))
                                subtotal = qty * price
                                total += subtotal

                                table_data.append([name, qty, f"₹{price}"])

                            st.markdown("#### ✅ Current Selection")

                            selected = st.session_state.get("selected_parameters", {})
                            total = 0

                            # Header row
                            header1, header2, header3 = st.columns([4, 1, 1])
                            header1.markdown("**Parameter Name**")
                            header2.markdown("**Qty**")
                            header3.markdown("**Price (₹)**")

                            # Data rows
                            for param in selected.values():
                                col1, col2, col3 = st.columns([4, 1, 1])
                                col1.write(param.get('name', 'Unnamed'))
                                col2.write(param.get('quantity', 0))
                                price = int(param.get('cost', 0))
                                col3.write(f"₹{price}")
                                total += int(param.get('quantity', 0)) * price

                            # Total
                            st.markdown("---")
                            st.markdown(f"### 💰 Grand Total: ₹{total}")

                        else:
                            st.info("⚠️ No parameters selected.")

                        if st.button("Generate Quotation"):
                            selected_param_data = []
                            for param_id, param_info in st.session_state.selected_parameters.items():
                                cost = param_info.get("cost") or 0
                                quantity = param_info.get("quantity") or 1  # default to 1 if missing
                                selected_param_data.append({
                                    "parameter_id": param_id,
                                    "name": param_info["name"],
                                    "cost": int(cost),
                                    "quantity": int(quantity)
                                })

                            customer_id = st.session_state.selected_customer_id
                            order = fetch_order_by_customer_id(customer_id)
                            order_id = order.get("id")
                            quotation_id = create_quotation(customer_id,order_id,selected_param_data)

                            if quotation_id:
                                save_selected_parameters_to_api(quotation_id)
                                st.success("✅ Quotation submitted successfully!")
                                st.session_state.selected_customer_id = None
                                st.session_state.selected_parameters = {}

                # ✅ Edit Form
                if st.session_state.show_form and st.session_state.customer_to_edit and \
                        st.session_state.customer_to_edit["id"] == customer_id:
                    customer_to_edit = st.session_state.customer_to_edit
                    order_comment = customer["order_req_comment"]
                    order_doc = customer["order_req_doc"]

                    with st.form(f"customer_form_{customer_id}"):
                        st.markdown("### 🛠️ Edit Customer Request")

                        c_name = st.text_input("Company Name",value=customer_to_edit["c_name"])
                        col1, col2 = st.columns(2)
                        name = col1.text_input("Person Name", value=customer_to_edit["name"])
                        email = col2.text_input("Email ID", value=customer_to_edit["email"])

                        col3, col4 = st.columns(2)
                        phone = col3.text_input("Phone Number", value=customer_to_edit["phone_number"])
                        whatsapp = col4.text_input("WhatsApp Number", value=customer_to_edit["whatsapp_number"])

                        address = st.text_area("Address", value=customer_to_edit["address"])

                        col5, col6 = st.columns(2)
                        comment = col5.text_area("Comment", value=order_comment)
                        document = col6.file_uploader("Upload Document", type=["pdf", "docx", "txt", "xlsx", "csv"],
                                                      key=f"edit_document_{customer_id}")

                        if order_doc:
                            st.write(f"Existing document: {order_doc}")

                        st.session_state.doc_check = order_doc

                        submit_btn = st.form_submit_button("✅ Submit")
                        cancel_btn = st.form_submit_button("❌ Cancel")

                    if submit_btn:
                        if name and email and phone and (comment or document):
                            updated_customer = {
                                "c_name" : c_name,
                                "name": name,
                                "email": email,
                                "phone_number": phone,
                                "whatsapp_number": whatsapp,
                                "address": address,
                                "is_delete": False
                            }
                            docfile = document if document else order_doc
                            order = fetch_order_by_customer_id(customer_id)
                            order_id = order.get("id")
                            update_customer_and_order(customer_id, order_id, updated_customer, comment, docfile)
                        else:
                            st.error("❌ Please fill all required fields and add a comment or document.")

                    if cancel_btn:
                        st.session_state.show_form = False
                        st.session_state.customer_to_edit = None
else:
    st.warning("🚫 Please log in to access this page.")
    st.switch_page("auth_pages/login.py")
