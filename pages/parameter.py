import os
import streamlit as st
import requests
from dotenv import load_dotenv
from perameter_add_in_database_shoertcut.add_parameter import insert_parameter_in_database
from perameter_add_in_database_shoertcut.unit_and_method_add import insert_unit_and_protocol

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL')
PARAMETER_URL = f"{API_BASE_URL}/parameter"

if "edit_param" not in st.session_state:
    st.session_state.edit_param = {}

def create_parameter(data):
    response = requests.post(f"{PARAMETER_URL}/", json=data)
    if response.status_code in [200, 201]:
        st.success("✅ Parameter added successfully!")
        st.rerun()
    else:
        st.error(f"❌ Failed to add parameter: {response.text}")

@st.cache_data(show_spinner="Fetching data...", ttl=600)
def fetch_parameters():
    response = requests.get(f"{PARAMETER_URL}/")
    return response.json() if response.status_code == 200 else []

para = fetch_parameters()
# st.code(para)
if not para :
    if st.button("insert Parameter in Database"):
        insert_parameter_in_database()
        insert_unit_and_protocol()
        st.cache_data.clear()  # 🚨 This clears all st.cache_data caches
        st.rerun()  # Optional: reruns the app to reflect cache-cleared state

def update_parameter(inx, parameter_id, message_placeholder):
    apha = st.session_state.get(f"edit_apha_{inx}", "")
    is3025 = st.session_state.get(f"edit_is3025_{inx}", "")
    unit = st.session_state.get(f"edit_unit_{inx}", "")

    if apha:
        is3025 = ""
    elif is3025:
        apha = ""

    data = {
        "name": st.session_state[f"input_name_{inx}"],
        "price": st.session_state[f"input_price_{inx}"],
        "min_range": st.session_state[f"input_min_{inx}"],
        "max_range": st.session_state[f"input_max_{inx}"],
        "unit": unit,
        "apha_24th_edition_method": apha or None,
        "is_3025_method": is3025 or None,
    }

    response = requests.put(f"{PARAMETER_URL}/{parameter_id}", json=data)
    if response.status_code == 200:
        message_placeholder.success("✅ Parameter updated successfully!")
        st.session_state.edit_param[inx] = False
    else:
        message_placeholder.error(f"❌ Failed to update parameter: {response.text}")

def delete_parameter(p_id, message_placeholder):
    response = requests.delete(f"{PARAMETER_URL}/{p_id}")
    if response.status_code == 200:
        message_placeholder.success("🗑️ Parameter deleted successfully!")
    else:
        message_placeholder.error(f"❌ Failed to delete parameter: {response.text}")

# --- Fetch and Filter Data ---
display_parameters = fetch_parameters()
search_query = st.text_input("🔍 Search Parameter by Name")
if search_query:
    display_parameters = [param for param in display_parameters if search_query.lower() in param['name'].lower()]

# --- Add Parameter Form ---
with st.form("add_parameter_form"):
    st.markdown("### ➕ Add Parameter Info")
    col1, col2 = st.columns([1, 1])

    p_id = col1.number_input("Parent Parameter Id", min_value=1)
    name = col1.text_input("Parameter Name")
    unit = col1.text_input("Unit")
    price = col1.text_input("Price")

    min_value = col1.number_input("Min Value", min_value=0)
    max_value = col2.number_input("Max Value", min_value=0)

    apha_protocol = col2.text_input("APHA 24th Edition Protocol")
    is3025_protocol = col2.text_input("IS 3025 Method Protocol")

    if apha_protocol:
        is3025_protocol = ""
    elif is3025_protocol:
        apha_protocol = ""

    submit_btn = col1.form_submit_button("✅ Submit Parameter Info")

    if submit_btn and name:
        payload = {
            "parent_id": p_id,
            "name": name,
            "unit": unit,
            "price": price,
            "min_range": min_value,
            "max_range": max_value,
            "apha_24th_edition_method": apha_protocol or None,
            "is_3025_method": is3025_protocol or None,
        }
        create_parameter(payload)

# --- Display Parameters ---
st.markdown("### 📄 Parameters List")
for ind, param in enumerate(display_parameters):
    with st.expander(f"Details of {param['name']}"):
        st.markdown(f"**🆔 ID:** {param['id']}")
        st.markdown(f"**🧩 Parent ID:** {param['parent_id']}")
        st.markdown(f"**📏 Unit:** {param.get('unit', 'N/A')}")
        st.markdown(f"**💰 Price:** {param.get('price', 'N/A')}")
        st.markdown(f"**🔢 Min Value:** {param.get('min_range', 'N/A')}")
        st.markdown(f"**🔢 Max Value:** {param.get('max_range', 'N/A')}")

        is_3025 = param.get("is_3025_method")
        apha = param.get("apha_24th_edition_method")

        if is_3025 and apha:
            protocol_display = f"{is_3025} | {apha}"
        elif is_3025:
            protocol_display = is_3025
        elif apha:
            protocol_display = apha
        else:
            protocol_display = "None"

        st.markdown(f"**📘 Protocol:** {protocol_display}")

        col5, col6, col7 = st.columns([2, 2, 3])
        if col6.button("✏️ Edit", key=f"edit_param_{ind}"):
            st.session_state.edit_param[ind] = True

        message_placeholder = st.empty()

        if col7.button("🗑️ Delete", key=f"delete_param_{ind}"):
            with st.form(f"delete_form_{ind}"):
                col11, col12, col13 = st.columns([2, 3, 1])
                col12.subheader("Are You Sure?")
                col2, col3, col4 = st.columns([2, 4, 4])
                if col3.form_submit_button("✅ YES", on_click=delete_parameter, args=(param['id'], message_placeholder)):
                    st.warning("🗑️ Data Deleted")
                    st.rerun()
                if col4.form_submit_button("❌ NO"):
                    st.success("✅ Deletion Cancelled")

        if st.session_state.edit_param.get(ind, False):
            with st.form(f"edit_param_form_{ind}"):
                col3, col4 = st.columns([1, 1])
                st.text_input("Edit Parameter Name", value=param['name'], key=f"input_name_{ind}")
                st.text_input("Edit Price", value=param['price'], key=f"input_price_{ind}")
                st.text_input("Edit Unit", value=param.get("unit", ""), key=f"edit_unit_{ind}")
                st.number_input("Edit Min Value", value=param['min_range'], key=f"input_min_{ind}")
                st.number_input("Edit Max Value", value=param['max_range'], key=f"input_max_{ind}")

                st.text_input("Edit APHA 24th Edition Protocol",
                              value=param.get("apha_24th_edition_method") or "",
                              key=f"edit_apha_{ind}")
                st.text_input("Edit IS 3025 Method Protocol",
                              value=param.get("is_3025_method") or "",
                              key=f"edit_is3025_{ind}")

                col5, col6, col7 = st.columns([1.5, 2, 3])
                update_btn = col6.form_submit_button("💾 Update Parameter",
                                                     on_click=update_parameter,
                                                     args=(ind, param['id'], message_placeholder))
                if update_btn:
                    st.rerun()

                cancel_btn = col7.form_submit_button("❌ Cancel Edit")
                if cancel_btn:
                    st.session_state.edit_param[ind] = False
