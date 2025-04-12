import streamlit as st
import pandas as pd

# Ensure session state variables are properly initialized
if "login" not in st.session_state:
    st.session_state.login = False
if "sample_form_data" not in st.session_state:
    st.session_state.sample_form_data = []
if "form_open" not in st.session_state:
    st.session_state.form_open = False
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# Login check
if st.session_state.login:
    # Page layout
    st.title("🧪 Sample Info")

    # Button to open form
    if st.button("➕ Add Sample Info"):
        st.session_state.form_open = True
        st.session_state.form_submitted = False  # Reset submission state

    # Display success message if form was submitted
    if st.session_state.form_submitted:
        st.success("✅ Form submitted successfully!")

    # Display the form if the flag is true
    if st.session_state.form_open:
        with st.form("water_testing_form"):
            col1, col2 = st.columns(2)

            # Left column → Customer details
            with col1:
                customer = st.text_input("🏠 Name & Address Customer", placeholder="Enter customer name and address")
                collection_date = st.date_input("📅 Date of Collection")
                receipt_date = st.date_input("📥 Date of Receipt")
                collected_by = st.text_input("👤 Sample Collected By", placeholder="Enter collector's name")
                particulars = st.text_input("📝 Sample Particulars", placeholder="Enter sample details")

            # Right column → More sample details
            with col2:
                location = st.text_input("📍 Location", placeholder="Enter location")
                quantity = st.text_input("📦 Sample Qty.", placeholder="Enter quantity")

            st.markdown("---")

            # Form buttons
            col_submit, col_cancel = st.columns(2)
            submit_btn = col_submit.form_submit_button("✅ Submit")
            cancel_btn = col_cancel.form_submit_button("❌ Cancel")

        # Form submission logic
        if submit_btn:
            st.session_state.form_open = False
            if all([customer, collection_date, receipt_date, collected_by, particulars, location, quantity]):
                form_entry = {
                    "Customer": customer,
                    "Collection Date": collection_date.strftime('%Y-%m-%d'),
                    "Receipt Date": receipt_date.strftime('%Y-%m-%d'),
                    "Collected By": collected_by,
                    "Particulars": particulars,
                    "Location": location,
                    "Quantity": quantity
                }

                # Store form data
                st.session_state.sample_form_data.append(form_entry)

                # Set form submitted flag
                st.session_state.form_submitted = True

                # Close the form
                st.session_state.form_open = False

            else:
                st.error("❌ Please fill in all required fields!")

        # Cancel button logic
        if cancel_btn:
            st.warning("🚫 Form submission cancelled.")
            st.session_state.form_open = False

    # Display submitted form data
    st.markdown("### 📄 Submitted Form Data:")

    if st.session_state.sample_form_data:
        df = pd.DataFrame(st.session_state.sample_form_data)
        st.dataframe(df)
    else:
        st.warning("⚠️ No data found")

else:
    # If not logged in, redirect to login page
    st.text("⚠️ Please login first.")
    st.switch_page('../auth_pages/login.py')
