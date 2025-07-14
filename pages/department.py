import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()

@st.cache_data(show_spinner="Fetching data...", ttl=600)
def get_departments():
    response = requests.get(f"{API_BASE_URL}/department/")
    return response.json() if response.status_code == 200 else []

API_BASE_URL = os.getenv('API_BASE_URL')

def add_department(department):
    return requests.post(f"{API_BASE_URL}/department", json=department)

def update_department(dept_id, department):
    return requests.put(f"{API_BASE_URL}/department/{dept_id}", json=department)

def delete_department(dept_id):
    return requests.delete(f"{API_BASE_URL}/department/{dept_id}")

# Session state for edit mode
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

st.title("🏢 Department Management System")

# 🔝 Add form
with st.form("add_form"):
    st.header("➕ Add Department")
    name = st.text_input("Department Name")
    location = st.text_input("Location")
    head_name = st.text_input("Head Name")
    submitted = st.form_submit_button("Add")

    if submitted:
        if name and location and head_name:
            dept = {
                "name": name,
                "location": location,
                "head_name": head_name,
                "is_deleted": False,
                "is_active": True
            }
            add_department(dept)
            st.success("Department added!")
            st.rerun()
        else:
            st.warning("Please fill all fields.")

# 📋 Department List
st.subheader("📋 Department List")
departments = get_departments()

if departments:
    for dept in departments:
        with st.expander(dept['name']):
            if st.session_state.edit_id == dept['id']:
                with st.form(f"edit_form_{dept['id']}"):
                    name = st.text_input("Department Name", value=dept['name'], key=f"name_{dept['id']}")
                    location = st.text_input("Location", value=dept['location'], key=f"location_{dept['id']}")
                    head_name = st.text_input("Head Name", value=dept['head_name'], key=f"head_{dept['id']}")
                    submit = st.form_submit_button("✅ Update")
                    if submit:
                        updated = {
                            "name": name,
                            "location": location,
                            "head_name": head_name,
                            "is_deleted": False,
                            "is_active": True
                        }
                        update_department(dept["id"], updated)
                        st.success("Department updated!")
                        st.session_state.edit_id = None
                        st.rerun()
            else:
                st.write(f"📍 **Location :** {dept['location']}")
                st.write(f"👤 **Head Name :** {dept['head_name']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{dept['id']}"):
                        st.session_state.edit_id = dept['id']
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{dept['id']}"):
                        delete_department(dept['id'])
                        st.success("Department deleted.")
                        st.rerun()

else:
    st.info("No departments found.")
