import streamlit as st
from component.nav import login_nav
from component.local_store import LocalStorageManager

storage=LocalStorageManager("user_login_status")

col1 ,col2  = st.columns([1,2])
col2.subheader("You are sure to log out !?")

col1 , col2 , col3 = st.columns([1,1,1])
if col2.button("Yes"):
    st.navigation(login_nav,position="hidden")
    storage.set_item("login_status",False)
    st.rerun()
if col3.button("No"):
    st.navigation([st.Page("Pages/Dashboard.py")])
    st.rerun()