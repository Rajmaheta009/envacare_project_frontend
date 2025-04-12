import streamlit as st
import pandas as pd

# Initialize session state
if "login" not in st.session_state:
    st.session_state.login = False
if "test_form_data" not in st.session_state:
    st.session_state.test_form_data = []
if "param_values" not in st.session_state:
    st.session_state.param_values = {}

# Login check
if st.session_state.login:
    st.title("🧪 Results Testing")

    # Static parameters with units
    parameters = {
        "pH Level": "pH",
        "Turbidity": "NTU",
        "Chlorine": "mg/L",
    }

    # Divider
    st.markdown("---")
    st.markdown("### 🔥 Enter Results for Parameters")

    # Table layout
    cols = st.columns([3, 2, 2])

    # Table headers
    cols[0].write("**Parameter Name**")
    cols[1].write("**Unit**")
    cols[2].write("**Result**")

    # Store input values
    results = []

    for param, unit in parameters.items():
        # Ensure session state for each parameter
        if param not in st.session_state.param_values:
            st.session_state.param_values[param] = {
                "result": ""
            }

        col1, col2, col3 = st.columns([3, 2, 2])

        col1.write(param)
        col2.write(unit)

        # Use session state to store values
        result = col3.text_input(f"Result - {param}",
                                 value=st.session_state.param_values[param]["result"],
                                 key=f"result_{param}")

        # Store the current values in session state
        st.session_state.param_values[param]["result"] = result

        # Append to results
        results.append({
            "Parameter": param,
            "Unit": unit,
            "Result": result
        })

    # Form buttons
    col_submit, col_cancel = st.columns(2)

    # Submit button logic
    if col_submit.button("✅ Submit"):
        # Ensure at least one result is filled
        if any(res["Result"].strip() for res in results):
            st.success("✅ Form submitted successfully!")

            # Store parameter data in session state
            st.session_state.test_form_data.extend(results)

            # Clear form values after submission
            for param in st.session_state.param_values:
                st.session_state.param_values[param]["result"] = ""
        else:
            st.warning("⚠️ Please enter at least one result before submitting.")

    # Cancel button logic
    if col_cancel.button("❌ Cancel"):
        st.warning("🚫 Form submission cancelled.")
        st.session_state.test_form_data = []

    # Display submitted data or show "No data found" message
    st.markdown("### 📄 Submitted Parameter Data:")

    if st.session_state.test_form_data:
        df = pd.DataFrame(st.session_state.test_form_data)
        st.dataframe(df)  # Use dataframe for better readability
    else:
        st.warning("⚠️ No data found")

else:
    # If not logged in, redirect to login page
    st.text("⚠️ Please login first.")
    st.switch_page('../auth_pages/login.py')
