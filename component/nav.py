import streamlit as st

nav_pages=[
    st.Page("pages/Dashboard.py", title= "Dashboard", default = True),
    st.Page("pages/Customer_request.py", title= "Customer Request"),
    st.Page("pages/Quotation.py", title= "Quotation List"),
    st.Page("pages/Sample.py", title= "Sample List"),
    st.Page("pages/invoice_list.py", title= "Invoice list"),
    st.Page("pages/department.py", title= "Department Set"),
    st.Page("pages/employee.py", title= "Employee Set"),
    st.Page("pages/parameter.py", title= "Parameter"),
    st.Page("pages/parameter_value_set.py", title= "Set Parameter Protocol And Range"),
    st.Page("pages/test.py", title= "TEST"),
    st.Page("pages/log_out.py", title= "Log Out"),
]

login_nav=[
    st.Page("auth_pages/login.py",title="login"),
    st.Page("pages/test.py",title="Test")
]
