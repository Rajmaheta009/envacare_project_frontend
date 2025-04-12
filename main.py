import streamlit as st
from component.local_store import LocalStorageManager
from component.nav import nav_pages,login_nav

# ✅ Initialize session state
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ✅ Sync LocalStorage with session state
storage=LocalStorageManager("user_login_status")
st.session_state.login = storage.get_item("login_status")

# ✅ Navigation Logic
if not st.session_state.login:
    # login_page = st.Page("auth_pages/login.py", title="Login")
    pg = st.navigation(login_nav,position="hidden")
    pg.run()
else:
    # st.navigation([st.Page("Pages/Dashboard.py")])
    pg = st.navigation(nav_pages)
    # st.switch_page("Dashboard.py")
    pg.run()
    # st.rerun()

