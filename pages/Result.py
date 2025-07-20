import streamlit as st
import requests
import os
from dotenv import load_dotenv

# --- Load API base URL ---
load_dotenv()
BASE_API = os.getenv("API_BASE_URL")

st.title("🧪 Lab Result Submission Portal")

# --- Fetch Orders ---
try:
    orders = requests.get(f"{BASE_API}/order").json()
    order_map = {order["order_number"]: order["id"] for order in orders}
    order_numbers = list(order_map.keys())
except Exception as e:
    st.error(f"Error fetching orders: {e}")
    st.stop()

# --- Select Order ---
selected_order_number = st.selectbox("Select Order Number", order_numbers)

if selected_order_number:
    order_id = order_map[selected_order_number]

    # --- Fetch Quotation ---
    quotation = requests.get(f"{BASE_API}/quotations/{order_id}").json()
    if not quotation:
        st.warning("No quotation found for this order.")
        st.stop()

    quotation_id = quotation["id"]

    # --- Fetch Order Parameters ---
    order_params = requests.get(f"{BASE_API}/order_parameters/op_id/{quotation_id}").json()

    st.subheader("🔬 Enter Results for Each Parameter")
    results_payload = []

    with st.form("submit_results"):
        # Table Header
        cols = st.columns([3, 1, 1, 3, 2, 2])
        cols[0].markdown("**Parameter Name**")
        cols[1].markdown("**Min**")
        cols[2].markdown("**Max**")
        cols[3].markdown("**Protocol Selection**")
        cols[4].markdown("**Method Used**")
        cols[5].markdown("**Result**")

        for param in order_params:
            param_id = param['parameter_id']
            param_details = requests.get(f"{BASE_API}/parameter/p_id/{param_id}").json()
            param_data = param_details[0]  # assume one

            name = param_data["name"]
            min_val = param_data.get("min_range", "-")
            max_val = param_data.get("max_range", "-")
            is_method = param_data.get("is_3025_method")
            apha_method = param_data.get("apha_24th_edition_method")

            row = st.columns([3, 1, 1, 3, 2, 2])
            row[0].markdown(name)
            row[1].markdown(str(min_val) if min_val else "-")
            row[2].markdown(str(max_val) if max_val else "-")

            protocol_key = f"protocol_{quotation_id}_{param_id}"
            method_key = f"method_{quotation_id}_{param_id}"
            result_key = f"result_{quotation_id}_{param_id}"

            # Protocol Section
            if is_method and apha_method:
                with row[3]:
                    st.markdown("**IS 3025 / APHA**")
                    selected_protocol = st.radio(
                        label="",
                        options=["IS 3025", "APHA"],
                        key=protocol_key,
                        horizontal=True,
                        label_visibility="collapsed"
                    )
            elif is_method:
                row[3].markdown("IS 3025")
                selected_protocol = "IS 3025"
            elif apha_method:
                row[3].markdown("APHA")
                selected_protocol = "APHA"
            else:
                row[3].markdown("-")
                selected_protocol = None

            method_used_input = row[4].text_input("Method Used", key=method_key)
            result_input = row[5].text_input("Result", key=result_key)

            # Final result value is selected protocol + result
            final_result = f"{selected_protocol} - {result_input}" if selected_protocol and result_input else result_input

            results_payload.append({
                "order_param_id": param["id"],
                "result": final_result.strip(),
                "protocol": selected_protocol,
                "method_used": method_used_input.strip()
            })

        submitted = st.form_submit_button("✅ Submit Results")

        if submitted:
            payload = [
                {
                    "order_param_id": r["order_param_id"],
                    "result": r["result"],
                    "protocol": r["protocol"],
                    "method_used": r["method_used"]
                }
                for r in results_payload if r["result"]
            ]
            if not payload:
                st.warning("Please enter at least one result.")
            else:
                response = requests.put(f"{BASE_API}/order_parameters/submit_results", json={"results": payload})
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
                if isinstance(res, dict) and res.get("result") not in [None, "None"]:
                    param_info = requests.get(f"{BASE_API}/parameter/p_id/{res['parameter_id']}").json()
                    param_data = param_info[0]
                    st.markdown(f"**🔹 Parameter Name:** {param_data['name']}")
                    st.markdown(f"**🔹 Protocol Used:** {res.get('protocol', 'N/A')}")
                    st.markdown(f"**🔹 Method Used:** {res.get('method_used', 'N/A')}")
                    st.markdown(f"**🔹 Result:** {res['result']}")
                    st.markdown("---")
                else:
                    st.write("Result is not filled, so no data is shown.")

            col1, col2 = st.columns(2)
            with col2:
                if st.button("⬇️ Download PDF"):
                    download_url = f"{BASE_API}/download_pdf/{quotation_id}"
                    st.markdown(f"[💾 Download PDF]({download_url})", unsafe_allow_html=True)
