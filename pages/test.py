import streamlit as st
from pages.Customer_request import customer_id,customer,fetch_parameters,render_parameters,render_filtered_parameters,QUOTATION_API
import requests

def handle_send_quotation(customer_id):
    if not st.session_state.selected_parameters:
        st.warning("Please select at least one parameter before sending quotation.")
        return

    total = sum(int(price) for price in st.session_state.selected_parameters.values())

    quotation_data = {
        "customer_id": customer_id,
        "parameters": list(st.session_state.selected_parameters.keys()),
        "prices": list(st.session_state.selected_parameters.values()),
        "total": total,
    }

    response =  requests.post(f"{QUOTATION_API}", json=quotation_data)

    if response.status_code == 200:
        st.success("Quotation sent successfully!")
        st.session_state.selected_customer_id = None
        st.session_state.selected_parameters.clear()
        st.rerun()
    else:
        st.error("Failed to send quotation.")


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

    # RIGHT COLUMN
    with col3:
        st.subheader("🧾 Selected Parameters")
        if "selected_parameters" not in st.session_state:
            st.session_state.selected_parameters = {}

        # Update the session state with selected parameters
        for key, value in selected_parameters.items():
            st.session_state.selected_parameters[key] = value

        total = 0
        for name, price in st.session_state.selected_parameters.items():
            st.write(f"✔️ {name} - ₹{price}")
            total += int(price)

        st.markdown(f"### 💰 Total: ₹{total}")

        if st.button("📤 Send Quotation", key=f"send_{customer_id}"):
            handle_send_quotation(customer_id)
