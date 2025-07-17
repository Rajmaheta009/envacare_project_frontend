import streamlit as st
import requests
import os
from dotenv import load_dotenv

# --- Load API base URL ---
load_dotenv()
BASE_API = os.getenv("API_BASE_URL")

st.title("Lab Result Submission Portal")

# --- Fetch orders ---
orders = requests.get(f"{BASE_API}/order").json()
order_map = {order["order_number"]: order["id"] for order in orders}
order_numbers = list(order_map.keys())

# --- Select Order ---
selected_order_number = st.selectbox("Select Order Number", order_numbers)

if selected_order_number:
    order_id = order_map[selected_order_number]

    # --- Fetch Quotation ---
    quotation = requests.get(f"{BASE_API}/quotations/{order_id}").json()

    if not quotation:
        st.warning("No quotation found for this order.")
    else:
        quotation_id = quotation["id"]

        # --- Fetch Order Parameters ---
        order_params = requests.get(f"{BASE_API}/order_parameters/op_id/{quotation_id}").json()

        st.subheader("🔬 Enter Results for Each Parameter")
        results_payload = []

        with st.form("submit_results"):
            # Header
            cols = st.columns([3, 1, 1, 2, 2])
            cols[0].markdown("**Parameter Name**")
            cols[1].markdown("**Min**")
            cols[2].markdown("**Max**")
            cols[3].markdown("**Protocol**")
            cols[4].markdown("**Result**")

            for param in order_params:
                param_details = requests.get(f"{BASE_API}/parameter/p_id/{param['parameter_id']}").json()
                param_data = param_details[0]  # assuming one result

                name = param_data["name"]
                min_val = param_data["min_range"]
                max_val = param_data["max_range"]
                protocol = param_data["protocol"]

                row = st.columns([3, 1, 1, 2, 2])
                row[0].markdown(name)
                row[1].markdown(str(min_val) if min_val is not None else "-")
                row[2].markdown(str(max_val) if max_val is not None else "-")
                row[3].markdown(protocol if protocol else "-")

                result_input = row[4].text_input("Result", key=f"result_{param['parameter_id']}")

                results_payload.append({
                    "parameter_id": param["parameter_id"],
                    "quotation_id": quotation_id,
                    "result": result_input
                })

            submitted = st.form_submit_button("✅ Submit Results")
            if submitted:
                payload = [r for r in results_payload if r["result"].strip() != ""]
                if not payload:
                    st.warning("Please enter at least one result.")
                else:
                    response = requests.post(f"{BASE_API}/submit_results", json={"results": payload})
                    if response.status_code == 200:
                        st.success("Results submitted successfully.")
                    else:
                        st.error("Failed to submit results.")

        # --- View Submitted Results ---
        st.subheader("📄 Submitted Results with PDF Options")
        submitted_results = requests.get(f"{BASE_API}/order_parameters/submitted_results/{quotation_id}").json()

        if not submitted_results:
            st.info("No submitted results found.")
        else:
            with st.expander(f"🧪 Order: {selected_order_number} - {len(submitted_results)} Parameters Submitted"):
                for res in submitted_results:
                    if res["result"]:
                        st.markdown(f"**🔹 Parameter ID:** {res['parameter_id']}")

                        # Fetch parameter name using the correct ID from `res`, not `param`
                        param_info = requests.get(f"{BASE_API}/parameter/p_id/{res['parameter_id']}").json()
                        param_data = param_info[0]
                        st.markdown(f"**🔹 Parameter Name:** {param_data['name']}")
                        st.markdown(f"**Result:** {res['result']}")
                        st.markdown("---")  # divider between parameters

                # One set of buttons at the end
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📄 View Full Order PDF"):
                        view_url = f"{BASE_API}/view_pdf/{quotation_id}"
                        st.markdown(f"[🔗 View PDF]({view_url})", unsafe_allow_html=True)
