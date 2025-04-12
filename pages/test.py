import streamlit as st
from pages.parameter import fetch_parameters
from streamlit.components.v1 import html
# Fetch all parameters
parameters = fetch_parameters()

# Split parent and child parameters
parent_parameters = [p for p in parameters if p["price"] is None]

# Create child mapping by parent_id
child_map = {}
for p in parameters:
    parent_id = p.get("parent_id")
    if parent_id is not None:
        child_map.setdefault(parent_id, []).append(p)

# Page layout
st.set_page_config(layout="wide")
st.title("🧪 Test Quotation Designer")

col1, col2 = st.columns([2, 1])
selected_parameters = {}

# Filter input

    # MODE 1: Normal hierarchy view when search is empty
def render_parameters(parent_id):
    children = child_map.get(parent_id, [])
    for child in children:
        if child["price"] is None:
            st.markdown(f"**{child['name']}**")
            render_parameters(child["id"])
        else:
            key = f"{child['id']}_{child['name']}"
            if st.checkbox(f"{child['name']} ₹{child['price']}", key=key):
                selected_parameters[child["name"]] = child["price"]
            else:
                selected_parameters.pop(child["name"], None)
            # html(select_parameter, height=100, scrolling=True)

# MODE 2: Filtered flat list view
def render_filtered_parameters():
    for p in parameters:
        if p["price"] is not None and search_term in p["name"].lower():
            key = f"{p['id']}_{p['name']}"
            if st.checkbox(f"{p['name']} ₹{p['price']}", key=key):
                selected_parameters[p["name"]] = p["price"]
            else:
                selected_parameters.pop(p["name"], None)


with col1:
    st.subheader("📌 Select Parameters")
    search_term = st.text_input("🔍 Filter by parameter name", "",).lower().strip()
    search_btn=st.button("Search")
    with st.container(height=500,border=False):
        if search_term == "":
            for parent in parent_parameters:
                if parent["parent_id"] is None:
                    st.markdown(f"### {parent['name']}")
                    render_parameters(parent["id"])
        else:
            render_filtered_parameters()

# RIGHT COLUMN
with col2:
    st.subheader("🧾 Selected Parameters")
    total = 0
    for name, price in selected_parameters.items():
        st.write(f"- {name}: ₹{price}")
        total += int(price)

    st.markdown("---")
    st.markdown(f"### 💰 Total Cost: ₹{total}")
