import os
import streamlit as st
import requests
from dotenv import load_dotenv
from perameter_add_in_database_shoertcut.add_parameter import insert_parameter_in_database
from perameter_add_in_database_shoertcut.unit_and_method_add import insert_unit_and_protocol
from collections import Counter
from typing import List

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

def update_parameter(inx, parameter_id, parent_id, message_placeholder):
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
        "parent_id": parent_id
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

def is_orphan_parameter(param: dict, all_params: List[dict]) -> bool:
    has_no_parent = param.get("parent_id") is None
    is_not_parent_of_any = all(p.get('parent_id') != param.get('name') for p in all_params)
    return has_no_parent and is_not_parent_of_any

para = fetch_parameters()
if not para:
    if st.button("insert Parameter in Database"):
        insert_parameter_in_database()
        insert_unit_and_protocol()
        st.cache_data.clear()
        st.rerun()

parent_name_map = {param["id"]: param["name"] for param in para}

# --- Add Parameter Form ---
with st.form("add_parameter_form"):
    st.markdown("### ➕ Add Parameter Info")
    col1, col2 = st.columns([1, 1])

    parent_options = [f"{p['id']}. {p['name']}" for p in para]
    parent_id_dropdown = col1.selectbox("Select Parent Parameter (optional)", options=["None"] + parent_options)
    manual_parent_id = col1.number_input("Or Enter Parent Parameter ID Manually", min_value=0)

    parent_id = int(parent_id_dropdown.split(".")[0]) if parent_id_dropdown != "None" else manual_parent_id

    name = col1.text_input("Parameter Name")
    unit = col1.text_input("Unit")
    price = col1.text_input("Price")
    min_value = col1.number_input("Min Value", min_value=0)
    max_value = col2.number_input("Max Value", min_value=0)

    apha_protocol = col2.text_input("APHA 24th Edition Protocol")
    is3025_protocol = col2.text_input("IS 3025 Method Protocol")

    submit_btn = col1.form_submit_button("✅ Submit Parameter Info")

    if submit_btn:
        if not apha_protocol and not is3025_protocol:
            st.warning("⚠️ Please add at least one protocol (APHA or IS 3025).")
        else:
            new_param = {
                "name": name,
                "unit": unit,
                "price": price,
                "min_range": min_value,
                "max_range": max_value,
                "apha_24th_edition_method": apha_protocol or None,
                "is_3025_method": is3025_protocol or None,
                "parent_id": parent_id if parent_id != 0 else None
            }

            if is_orphan_parameter(new_param, para):
                st.warning("⚠️ You are making this parameter a parent. Do you want to proceed?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.form_submit_button("✅ Yes, Save"):
                        create_parameter(new_param)
                with col_no:
                    if st.form_submit_button("❌ No, Cancel"):
                        st.info("Cancelled.")
                        st.rerun()
            else:
                create_parameter(new_param)

# --- Display Parameters ---
st.markdown("### 📄 Parameters List")
display_parameters = fetch_parameters()
search_query = st.text_input("🔍 Search Parameter by Name")
if search_query:
    display_parameters = [p for p in display_parameters if search_query.lower() in p['name'].lower()]

for ind, param in enumerate(display_parameters):
    parent_name = parent_name_map.get(param.get("parent_id"), "None")
    with st.expander(f"🔗 Parent: {parent_name} ➤ Parameter: {param['name']}"):
        st.markdown(f"**🆔 ID:** {param['id']}")
        st.markdown(f"**🧩 Parent ID:** {param.get('parent_id', 'None')}")
        st.markdown(f"**📏 Unit:** {param.get('unit', 'N/A')}")
        st.markdown(f"**💰 Price:** {param.get('price', 'N/A')}")
        st.markdown(f"**🔢 Min Value:** {param.get('min_range', 'N/A')}")
        st.markdown(f"**🔢 Max Value:** {param.get('max_range', 'N/A')}")

        is_3025 = param.get("is_3025_method")
        apha = param.get("apha_24th_edition_method")
        st.markdown(f"**📘 Protocol:** {is_3025 or ''} {('| ' + apha) if apha and is_3025 else apha or 'None'}")

        col5, col6, col7 = st.columns([2, 2, 3])
        if col6.button("✏️ Edit", key=f"edit_param_{ind}"):
            st.session_state.edit_param[ind] = True

        message_placeholder = st.empty()
        if col7.button("🗑️ Delete", key=f"delete_param_{ind}"):
            with st.form(f"delete_form_{ind}"):
                col2, col3 = st.columns(2)
                if col2.form_submit_button("✅ YES", on_click=delete_parameter, args=(param['id'], message_placeholder)):
                    st.rerun()
                if col3.form_submit_button("❌ NO"):
                    st.success("✅ Deletion Cancelled")

        if st.session_state.edit_param.get(ind, False):
            with st.form(f"edit_param_form_{ind}"):
                # st.text_input("Edit Parameter Name", value=param['name'], key=f"input_name_{ind}")
                parent_dropdown_options = ["None"] + [f"{p['id']}. {p['name']}" for p in para]
                current_parent_value = next((f"{p['id']}. {p['name']}" for p in para if p['id'] == param.get('parent_id')), "None")
                selected_parent = st.selectbox("Edit Parent Parameter", options=parent_dropdown_options, index=parent_dropdown_options.index(current_parent_value), key=f"edit_parent_select_{ind}")
                parent_id = int(selected_parent.split(".")[0]) if selected_parent != "None" else None
                st.text_input("Edit Price", value=param['price'], key=f"input_price_{ind}")
                st.text_input("Edit Unit", value=param.get("unit", ""), key=f"edit_unit_{ind}")
                st.number_input("Edit Min Value", value=param['min_range'], key=f"input_min_{ind}")
                st.number_input("Edit Max Value", value=param['max_range'], key=f"input_max_{ind}")
                st.text_input("Edit APHA 24th Edition Protocol", value=param.get("apha_24th_edition_method") or "", key=f"edit_apha_{ind}")
                st.text_input("Edit IS 3025 Method Protocol", value=param.get("is_3025_method") or "", key=f"edit_is3025_{ind}")


                col_update, col_cancel = st.columns([2, 2])
                if col_update.form_submit_button("💾 Update Parameter"):
                    update_parameter(ind, param['id'], parent_id, message_placeholder)
                    st.rerun()
                if col_cancel.form_submit_button("❌ Cancel Edit"):
                    st.session_state.edit_param[ind] = False
