import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL")

PARAM_API = f"{API_BASE_URL}/parameter"

st.title("Edit Parameter Values")

# Fetch parameter data
response = requests.get(PARAM_API)
if response.status_code != 200:
    st.error("Failed to fetch parameters.")
    st.stop()

data = response.json()

# Build lookup for parent names
id_to_name = {p["id"]: p["name"] for p in data}

# Filter: Only parameters whose ID is NOT used as any other parameter's parent_id
used_as_parent = {p.get("parent_id") for p in data if p.get("parent_id") is not None}
leaf_params = [p for p in data if p["id"] not in used_as_parent]

# Build dropdown list: parameter name (parent name)
display_names = []
param_lookup = {}

for p in leaf_params:
    parent_name = id_to_name.get(p.get("parent_id"), "")
    display_name = f"{p['name']} ({parent_name})" if parent_name else p['name']
    display_names.append(display_name)
    param_lookup[display_name] = p

# Dropdown
selected_display = st.selectbox("Select Parameter", display_names)
selected_param = param_lookup[selected_display]

# Form to edit min, max, and protocol
with st.form("parameter_form"):
    min_val = st.number_input(
        "Min Value",
        value=float(selected_param["min_range"]) if selected_param["min_range"] is not None else 0.0,
        min_value=0.0
    )
    max_val = st.number_input(
        "Max Value",
        value=float(selected_param["max_range"]) if selected_param["max_range"] is not None else 0.0,
        min_value=0.0
    )
    protocol = st.text_input(
        "Protocol",
        value=selected_param["protocol"] if selected_param["protocol"] else ""
    )

    submit = st.form_submit_button("Submit")

# Submit the edited data
if submit:
    try:
        payload = {
            "parameter_id": selected_param["id"],
            "name": selected_param["name"],
            "price": selected_param.get("price", 0.0),
            "min_range": float(min_val) if min_val else None,
            "max_range": float(max_val) if max_val else None,
            "protocol": protocol if protocol else None
        }

        res = requests.put(f"{PARAM_API}/{selected_param['id']}", json=payload)

        if res.status_code == 200:
            st.success("Parameter values updated successfully.")
            st.rerun()
        else:
            st.error(f"Failed to submit values. Status Code: {res.status_code}")
    except ValueError:
        st.error("Min and Max values must be numeric.")
