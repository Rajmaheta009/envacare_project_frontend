import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL')


# --- API Functions ---
def get_employees():
    response = requests.get(f"{API_BASE_URL}/employee/")
    return response.json() if response.status_code == 200 else []


def add_employee(employee):
    return requests.post(f"{API_BASE_URL}/employee", json=employee)


def update_employee(emp_id, employee):
    return requests.put(f"{API_BASE_URL}/employee/{emp_id}", json=employee)


def delete_employee(emp_id):
    return requests.delete(f"{API_BASE_URL}/employee/{emp_id}")


# --- Department Fetch for Dropdown ---
def get_departments():
    res = requests.get(f"{API_BASE_URL}/department/")
    return res.json() if res.status_code == 200 else []


# --- Session state for edit mode ---
if "emp_edit_id" not in st.session_state:
    st.session_state.emp_edit_id = None

st.title("👨‍💼 Employee Management System (with API)")

# --- Add Employee Form ---
with st.form("add_employee_form"):
    st.header("➕ Add Employee")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    phone = st.text_input("Phone Number")

    # Department Dropdown
    dept_list = get_departments()
    dept_options = {dept["name"]: dept["id"] for dept in dept_list}
    dept_name = st.selectbox("Select Department", list(dept_options.keys()))
    dept_id = dept_options[dept_name]

    submitted = st.form_submit_button("Add")

    if submitted:
        if name and email and password and phone:
            employee = {
                "name": name,
                "email": email,
                "password": password,
                "phone_number": phone,
                "dept_id": dept_id,
                "is_deleted": False,
                "is_active": True
            }
            add_employee(employee)
            st.success("Employee added successfully!")
            st.rerun()
        else:
            st.warning("Please fill all fields.")

# --- Employee List ---
st.subheader("📋 Employee List")
employees = get_employees()

if employees:
    for emp in employees:
        with st.expander(f"{emp['name']} - {emp['email']}"):
            if st.session_state.emp_edit_id == emp['id']:
                # Edit Form
                with st.form(f"edit_emp_form_{emp['id']}"):
                    name = st.text_input("Name", value=emp['name'], key=f"name_{emp['id']}")
                    email = st.text_input("Email", value=emp['email'], key=f"email_{emp['id']}")
                    password = st.text_input("Password", type="password", value=emp['password'],
                                             key=f"pass_{emp['id']}")
                    phone = st.text_input("Phone Number", value=emp['phone_number'], key=f"phone_{emp['id']}")

                    dept_name = next((d["name"] for d in dept_list if d["id"] == emp["dept_id"]), None)
                    selected_dept = st.selectbox("Select Department", list(dept_options.keys()),
                                                 index=list(dept_options.keys()).index(dept_name))

                    if st.form_submit_button("✅ Update"):
                        updated = {
                            "name": name,
                            "email": email,
                            "password": password,
                            "phone_number": phone,
                            "dept_id": dept_options[selected_dept],
                            "is_deleted": False,
                            "is_active": True
                        }
                        update_employee(emp["id"], updated)
                        st.success("Employee updated!")
                        st.session_state.emp_edit_id = None
                        st.rerun()
            else:
                st.write(f"📧 **Email:** {emp['email']}")
                st.write(f"📱 **Phone:** {emp['phone_number']}")
                dept_name = next((d["name"] for d in dept_list if d["id"] == emp["dept_id"]), "N/A")
                st.write(f"🏢 **Department:** {dept_name}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{emp['id']}"):
                        st.session_state.emp_edit_id = emp['id']
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{emp['id']}"):
                        delete_employee(emp['id'])
                        st.success("Employee deleted.")
                        st.rerun()
else:
    st.info("No employees found.")
