import os
import requests
import streamlit as st
from component.local_store import LocalStorageManager
from component.nav import login_nav

# Local storage for login status
storage = LocalStorageManager("user_login_status")

# Backend API
API_BASE_URL = os.getenv('API_BASE_URL')
LOGIN_URL = f"{API_BASE_URL}/auth/login"
REGISTER_URL = f"{API_BASE_URL}/auth/register"

# App Title and Logo
col1, col2, col3 = st.columns([1.3, 1, 1])
col1.image("static/logo.png", width=150)

# Page title
col4, col5 = st.columns([2, 3])
col4.title("Login / Register")

# Session toggle for register
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# Toggle buttons

# 💡 Registration Form
if st.session_state.show_register:
    st.subheader("Create New Account")
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_btn = st.form_submit_button("Create Account")

    if register_btn:
        if password != confirm_password:
            st.warning("⚠️ Passwords do not match.")
        else:
            res = requests.post(REGISTER_URL, json={
                "username": username,
                "email": email,
                "password": password
            })
            if res.status_code == 200:
                st.success("✅ Registration successful! Please login.")
                st.session_state.show_register = False
                st.rerun()
            else:
                st.error("❌ Registration failed. Try again.")

# 🔐 Login Form
else:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        res = requests.post(LOGIN_URL, json={"email": email, "password": password})
        if res.status_code == 200:
            data = res.json()
            st.session_state.username = data.get("username", "")
            st.session_state.user_id = data.get("id", "")
            storage.set_item("login_status", True)
            st.success("✅ Login successful! Redirecting...")

            main = st.Page("main.py", title="main")
            pg = st.navigation([main], position="hidden")
            pg.run()
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")
col6, col7 = st.columns(2)
if col6.button("🔑 Login"):
    st.session_state.show_register = False
if col7.button("📝 Register"):
    st.session_state.show_register = True
