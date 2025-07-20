import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL")
PARAM_API = f"{API_BASE_URL}/parameter"

st.title("Edit Parameter Values")

with st.spinner("Fetching parameters..."):
    response = requests.get(PARAM_API)
    if response.status_code != 200:
        st.error("Failed to fetch parameters.")
        st.stop()

data = response.json()

# Lookup parent names
id_to_name = {p["id"]: p["name"] for p in data}
used_as_parent = {p.get("parent_id") for p in data if p.get("parent_id") is not None}
leaf_params = [p for p in data if p["id"] not in used_as_parent]

# Build selectbox
display_names = []
param_lookup = {}

for p in leaf_params:
    parent_name = id_to_name.get(p.get("parent_id"), "")
    display_name = f"{p['name']} ({parent_name})" if parent_name else p['name']
    display_names.append(display_name)
    param_lookup[display_name] = p

selected_param = None

if display_names:
    selected_display = st.selectbox("Select Parameter", display_names)
    selected_param = param_lookup.get(selected_display)

    if selected_param is None:
        st.error("Selected parameter not found.")
        st.stop()
    else:
        st.success(f"Selected: {selected_display}")
else:
    st.warning("No parameters available.")
    st.stop()

# Form to edit
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

    # Get current protocol values as string
    is_3025_value = selected_param.get("is_3025_method", "")
    apha_value = selected_param.get("apha_24th_edition_method", "")

    is_3025_input = st.text_input("IS 3025 Method", value=is_3025_value if is_3025_value else "")
    apha_input = st.text_input("APHA 24th Edition Method", value=apha_value if apha_value else "")

    submit = st.form_submit_button("✅ Submit")

# Submit
if submit:
    try:
        payload = {
            "parameter_id": selected_param["id"],
            "name": selected_param["name"],
            "price": selected_param.get("price", 0.0),
            "min_range": float(min_val),
            "max_range": float(max_val),
            "is_3025_method": is_3025_input.strip() if is_3025_input.strip() else None,
            "apha_24th_edition_method": apha_input.strip() if apha_input.strip() else None
        }

        res = requests.put(f"{PARAM_API}/{selected_param['id']}", json=payload)

        if res.status_code == 200:
            st.success("Parameter values updated successfully.")
            st.rerun()
        else:
            st.error(f"Failed to submit values. Status Code: {res.status_code}")
            st.write(payload)
    except ValueError:
        st.error("Min and Max values must be numeric.")
