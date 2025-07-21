import streamlit as st
import requests
import os
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO

# Load environment variables
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
        header = st.columns([0.5, 2.5, 1, 1, 1, 2.5, 2.5, 2])
        header[0].markdown("**No.**")
        header[1].markdown("**Parameter Name**")
        header[2].markdown("**Min**")
        header[3].markdown("**Max**")
        header[4].markdown("**Unit**")
        header[5].markdown("**Protocol**")
        header[6].markdown("**Home Method**")
        header[7].markdown("**Result**")

        # We keep track of param info for export later
        param_info_map = {}

        for i, param in enumerate(order_params, start=1):
            param_id = param['parameter_id']
            param_details = requests.get(f"{BASE_API}/parameter/p_id/{param_id}").json()
            param_data = param_details[0]

            name = param_data["name"]
            unit = param_data.get("unit", "-")
            min_val = param_data.get("min_range", "-")
            max_val = param_data.get("max_range", "-")
            is_method = param_data.get("is_3025_method")
            apha_method = param_data.get("apha_24th_edition_method")

            row = st.columns([0.5, 2.5, 1, 1, 1, 2.5, 2.5, 2])
            row[0].markdown(str(i))
            row[1].markdown(name)
            row[2].markdown(str(min_val) if min_val else "-")
            row[3].markdown(str(max_val) if max_val else "-")
            row[4].markdown(unit or "-")

            # --- Dynamic protocol display from DB ---
            protocol_options = []
            if is_method:
                protocol_options.append(is_method)
            if apha_method:
                protocol_options.append(apha_method)

            protocol_radio_key = f"radio_protocol_{quotation_id}_{param_id}"
            selected_protocol = row[5].radio(
                label="",
                options=protocol_options,
                key=protocol_radio_key,
                horizontal=True,
                label_visibility="collapsed"
            )

            # Home protocol input
            home_protocol_key = f"home_protocol_{quotation_id}_{param_id}"
            home_protocol = row[6].text_input(
                label="",
                key=home_protocol_key,
                label_visibility="collapsed",
                placeholder="Type home protocol"
            )

            # Result input
            result_key = f"result_{quotation_id}_{param_id}"
            result = row[7].text_input("Result", key=result_key)


            results_payload.append({
                "order_param_id": param["id"],
                "parameter_id": param_id,
                "result": result.strip(),
                "protocol_used": selected_protocol,
                "home_protocol": home_protocol.strip(),
                "name": name,
                "unit": unit or "-"
            })

            # Save param info for export filtering
            param_info_map[param["id"]] = {
                "name": name,
                "unit": unit or "-"
            }

        submitted = st.form_submit_button("✅ Save Result")

        if submitted:
            missing_results = [res for res in results_payload if not res["result"]]

            if missing_results:
                st.error("❌ Please fill in the Result field for all parameters before submitting.")
                st.stop()
            else:
                success_count = 0

            for res_data in results_payload:
                if res_data["result"]:
                    url = f"{BASE_API}/order_parameters/result/{quotation_id}/{res_data['parameter_id']}"

                    # ✅ Correct logic
                    if res_data["home_protocol"]:
                        st.write("hlpppp")# If Home Method is filled
                        protocol_used = res_data["home_protocol"]  # Save home protocol as the official protocol
                        home_protocol = res_data["home_protocol"]
                    else:  # If Home Method is empty
                        # st.write("hlpppp")
                        protocol_used = res_data["protocol_used"]  # Save selected radio button
                        home_protocol = ""  # Nothing typed in home

                    payload = {
                        "result": res_data["result"],
                        "protocol_used": protocol_used,
                        "home_protocol": home_protocol
                    }

                    res = requests.put(url, json=payload)

                    if res.status_code == 200:
                        success_count += 1
                    else:
                        st.warning(f"⚠️ Failed for Parameter ID {res_data['parameter_id']}")

            st.success(f"✅ Successfully updated {success_count} result(s).")

    # --- Expander to show saved results where result is NOT NULL ---
    saved_results = [r for r in results_payload if r["result"]]

    if saved_results:
        with st.expander("📄 View Saved Results"):
            # Create dataframe for display and export
            data_for_export = []
            for idx, res in enumerate(saved_results, start=1):
                # ✅ Decide which protocol to show
                protocol_display = res["home_protocol"] if res["home_protocol"] else res["protocol_used"]

                # ✅ Append row to export data
                data_for_export.append({
                    "Sr. No": idx,
                    "Parameter": res["name"],
                    "Result": res["result"],
                    "Unit": res["unit"],
                    "Protocol": protocol_display
                })

            df = pd.DataFrame(data_for_export)
            st.table(df)


            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Results')
                processed_data = output.getvalue()
                return processed_data


            # Generate the Excel binary
            excel_data = to_excel(df)

            # Streamlit download button
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"saved_results_order_{order_numbers}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )