import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:8000"
PARAMETER_URL = f"{BASE_URL}/parameter"
PARENT_PARAMETER_URL = f"{BASE_URL}/parent_parameter"

if "edit_form" not in st.session_state:
    st.session_state.edit_form = None
if "edit_param" not in st.session_state:
    st.session_state.edit_param = {}
if "edit_parent_" not in st.session_state:
    st.session_state.edit_parent_ = {}
if "delete_param" not in st.session_state:
    st.session_state.delete_param = {}
if "delete_parent_" not in st.session_state:
    st.session_state.delete_parent_ = {}


def create_parameter(data):
    response = requests.post(f"{PARAMETER_URL}/", json=data)
    if response.status_code in [200, 201]:
        st.success("Parameter added successfully!")
        st.rerun()
    else:
        st.error(f"Failed to add parameter: {response.text}")

def fetch_parameters():
    response = requests.get(PARAMETER_URL)
    return response.json() if response.status_code == 200 else []


def update_parameter(inx, parameter_id, message_placeholder):
    data = {
        "name": st.session_state[f"input_name_{inx}"],
        "price": st.session_state[f"input_price_{inx}"],
        "min_range": st.session_state[f"input_min_{inx}"],
        "max_range": st.session_state[f"input_max_{inx}"],
        "protocol": st.session_state[f"input_protocol_{inx}"]
    }
    response = requests.put(f"{PARAMETER_URL}/{parameter_id}", json=data)
    if response.status_code == 200:
        message_placeholder.success("Parameter updated successfully!")
        st.session_state.edit_param[inx] = False
        # st.rerun()
    else:
        message_placeholder.error(f"Failed to update parameter: {response.text}")


def delete_parameter(p_id, message_placeholder):
    response = requests.delete(f"{PARAMETER_URL}/{p_id}")
    if response.status_code == 200:
        message_placeholder.success("Parameter deleted successfully!")
        # st.rerun()
    else:
        message_placeholder.error(f"Failed to delete parameter: {response.text}")

# Fetch data once
display_parameters = fetch_parameters()

# Add Parameter Form
with st.form("add_parameter_form"):
    st.markdown("### Add Parameter Info")

    col1 , col2 = st.columns([1,1])
    p_id = col1.number_input("Parent Parameter Id",min_value=1)
    name = col1.text_input("Parameter Name")
    protocol = col2.text_input("Protocol Name")
    min_value = col1.number_input("Min Value", min_value=10)
    max_value = col2.number_input("Max Value", min_value=100)
    price = col1.text_input("Price")
    submit_btn = col1.form_submit_button("✅ Submit Parameter Info")
    if submit_btn and name:
        create_parameter({"parent_id":p_id,"name": name, "price": price, "min_range": min_value, "max_range": max_value, "protocol": protocol})
        st.rerun()

# Display Parameters
st.markdown("### Parameters")
for ind, param in enumerate(display_parameters):
    with st.expander(f"Details of {param['name']}"):
        st.markdown(f"**Id:** {param['id']}")
        st.markdown(f"**Parent Id:** {param['parent_id']}")
        st.markdown(f"**Price:** {param.get('price', 'N/A')}")
        st.markdown(f"**Min Value:** {param.get('min_range', 'N/A')}")
        st.markdown(f"**Max Value:** {param.get('max_range', 'N/A')}")
        st.markdown(f"**Protocol:** {param.get('protocol', 'N/A')}")

        col5, col6, col7 = st.columns([2, 2, 3])
        if col6.button("Edit", key=f"edit_param_{ind}"):
            st.session_state.edit_param[ind] = True

        message_placeholder = st.empty()  # Create a placeholder

        if col7.button("Delete", key=f"delete_param_{ind}"):
            with st.form("delete?"):
                col11,col12,col13 = st.columns([2,3,1])
                col12.subheader("Are You Sure")
                col2, col3 ,col4 = st.columns([2,4,4])
                if col3.form_submit_button("YES",on_click=delete_parameter,args=(param['id'], message_placeholder)):
                    st.warning("data is deleted")
                if col4.form_submit_button("NO"):
                    st.success("Data Is Not Deleted")


        if st.session_state.edit_param.get(ind, False):
            with st.form(f"edit_param_form_{ind}"):
                col3, col4 = st.columns([1, 1])
                edit_name = col3.text_input("Edit Parameter Name", value=param['name'], key=f"input_name_{ind}")
                edit_protocol = col4.text_input("Edit Protocol Name", value=param['protocol'],key=f"input_protocol_{ind}")
                edit_min = col3.number_input("Edit Min Value", value=(param['min_range']), key=f"input_min_{ind}")
                edit_max = col4.number_input("Edit Max Value", value=(param['max_range']), key=f"input_max_{ind}")
                edit_price = col3.text_input("Edit Price", value=(param['price']), key=f"input_price_{ind}")

                col5 ,col6, col7= st.columns([1.5,2,3])
                update_btn = col6.form_submit_button("Update Parameter",
                                                   on_click=update_parameter,
                                                   args=(ind, param['id'], message_placeholder))
                if update_btn:
                    st.rerun()
                cancel_btn = col7.form_submit_button("Cancel Edit")
                if cancel_btn:
                    st.session_state.edit_param[ind] = False