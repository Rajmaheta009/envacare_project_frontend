import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import os
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone

# Load API base
load_dotenv()
BASE_API = os.getenv("API_BASE_URL")

# Session state setup
if 'selected_params' not in st.session_state:
    st.session_state.selected_params = []
if 'saved_results' not in st.session_state:
    st.session_state.saved_results = []
if "recent_batch_results" not in st.session_state:
    st.session_state.recent_batch_results = []
if "show_history" not in st.session_state:
    st.session_state.show_history = False
if "selected_group_data" not in st.session_state:
    st.session_state.selected_group_data = []

# Page title
st.title("🧪 Lab Parameter Entry")

# Layout
main_col, side_col = st.columns([4, 2], gap="large")

# ------------------------ MAIN COLUMN ------------------------ #
with main_col:
    search = st.text_input("🔍 Search Parameter")
    try:
        all_params = requests.get(f"{BASE_API}/parameter").json()
        filtered = [p for p in all_params if search.lower() in p["name"].lower()] if search else all_params
    except:
        st.error("❌ Cannot load parameters")
        filtered = []

    st.markdown("### ✅ Select Parameters to Enter Result")
    with st.container(height=400):
        for param in filtered:
            checkbox_state = st.checkbox(param["name"], key=f"check_{param['id']}", value=param in st.session_state.selected_params)
            if checkbox_state and param not in st.session_state.selected_params:
                st.session_state.selected_params.append(param)
            elif not checkbox_state and param in st.session_state.selected_params:
                st.session_state.selected_params.remove(param)

    if st.session_state.selected_params:
        st.markdown("---")
        st.markdown("### ✍️ Result Entry Table")

        # Removed Min and Max columns
        header_cols = st.columns([0.5, 2.5, 0.7, 2, 1.5, 1.5])
        headers = ["No.", "Parameter Name", "Unit", "Protocol Use For Analysis", "Home Method", "Result"]
        for col, h in zip(header_cols, headers):
            col.markdown(f"**{h}**")

        for idx, param in enumerate(st.session_state.selected_params, start=1):
            row_cols = st.columns([0.5, 2.5, 0.7, 2, 1.5, 1.5])
            with row_cols[0]: st.markdown(str(idx))
            with row_cols[1]: st.markdown(param["name"])
            # with row_cols[2]: st.markdown(str(param.get("min_value", "•")))
            # with row_cols[3]: st.markdown(str(param.get("max_value", "•")))
            with row_cols[2]: st.markdown(param.get("unit", "•"))

            protocol_options = []
            if param.get("is_3025_method"):
                protocol_options.append(param.get("is_3025_method"))
            if param.get("apha_24th_edition_method"):
                protocol_options.append(param.get("apha_24th_edition_method"))
            with row_cols[3]:
                if protocol_options:
                    st.radio(" ", protocol_options, key=f"protocol_{param['id']}", horizontal=True, label_visibility="collapsed")
                else:
                    st.markdown("`No options to select.`")
            with row_cols[4]: st.text_input("Home Method", key=f"method_{param['id']}", label_visibility="collapsed")
            with row_cols[5]: st.text_input("Result", key=f"result_{param['id']}", label_visibility="collapsed")

        # ✅ Save Result Button with Reset Logic
        if st.button("✅ Save Result"):
            recent_batch = []
            successful_params = []

            for param in st.session_state.selected_params:
                result_key = f"result_{param['id']}"
                method_key = f"method_{param['id']}"
                protocol_key = f"protocol_{param['id']}"

                result = st.session_state.get(result_key, "").strip()
                unit = param.get("unit", "")
                method = st.session_state.get(method_key, "").strip()
                protocol = st.session_state.get(protocol_key, "").strip()

                if not result:
                    st.warning(f"⚠️ Please enter result for: {param['name']}")
                    continue

                final_protocol = method if method else protocol

                payload = {
                    "parameter_name": param["name"],
                    "unit": unit,
                    "result": result,
                    "protocol_use_for_analysis": final_protocol,
                }

                try:
                    res = requests.post(f"{BASE_API}/quick_result/re", json=payload)
                    if res.status_code == 200:
                        st.success(f"✅ Saved: {param['name']}")
                        store_protocol = final_protocol
                        entry = {
                            "Name": param["name"],
                            # "Min": param.get("min_value", ""),
                            # "Max": param.get("max_value", ""),
                            "Unit": unit,
                            "Protocol": store_protocol,
                            "Result": result
                        }
                        st.session_state.saved_results.append(entry)
                        recent_batch.append(entry)
                        successful_params.append(param)
                    else:
                        st.error(f"❌ Failed to save: {param['name']}")
                except Exception as e:
                    st.error(f"⚠️ Error for {param['name']}: {e}")

            # ✅ Add recent batch and clean up UI for saved
            if recent_batch:
                st.session_state.recent_batch_results = recent_batch

            # ✅ Clear saved parameters' form controls
            for param in successful_params:
                for key in [f"check_{param['id']}", f"protocol_{param['id']}", f"method_{param['id']}",
                            f"result_{param['id']}"]:
                    if key in st.session_state:
                        del st.session_state[key]

            # ✅ Only keep unsaved ones for next form render
            st.session_state.selected_params = [
                p for p in st.session_state.selected_params if p not in successful_params
            ]

            st.rerun()  # rerender UI clean

    if st.session_state.saved_results:
        st.markdown("### 📊 Submitted Results")
        df = pd.DataFrame(st.session_state.saved_results)
        st.dataframe(df, use_container_width=True)

        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        excel_data = to_excel(df)
        st.download_button("📥 Download Excel", data=excel_data, file_name="results.xlsx")

    if st.session_state.recent_batch_results:
        st.markdown("### 🆕 Recently Saved Parameters")
        df_recent = pd.DataFrame(st.session_state.recent_batch_results)
        st.dataframe(df_recent, use_container_width=True)

        def to_excel_recent(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        excel_recent_data = to_excel_recent(df_recent)
        st.download_button("📥 Download Recent Batch", data=excel_recent_data, file_name="recent_results.xlsx")

# ------------------------ HISTORY PANEL ------------------------ #
with side_col:
    col1, col2 = st.columns([7, 2])

    if col2.button("🔄"):
        with st.spinner("🔄 Resetting the app. Please wait..."):
            st.session_state.selected_params = []
            st.session_state.saved_results = []
            st.session_state.recent_batch_results = []
            st.session_state.show_history = False
            st.session_state.selected_group_data = []
            st.rerun()

    if col1.button("📜 Toggle History"):
        st.session_state.show_history = not st.session_state.show_history

    if st.session_state.show_history:
        st.markdown("## 📚 Filter History")
        try:
            res = requests.get(f"{BASE_API}/quick_result/")  # Fetch history data from API
            res.raise_for_status()
            df_hist = pd.DataFrame(res.json())

            if df_hist.empty:
                st.info("ℹ️ No records available.")
            else:
                ist = timezone('Asia/Kolkata')
                df_hist["parsed_time"] = pd.to_datetime(df_hist["current_time_date"]).dt.tz_localize('UTC').dt.tz_convert(ist)
                df_hist["timestamp_group"] = df_hist["parsed_time"].dt.strftime("%d-%m-%Y %I:%M:%S %p")

                with st.container(height=400):
                    colf1, colf2 = st.columns(2)
                    with colf1:
                        selected_date = st.date_input("📅 Select Date to Filter", key="hist_date")
                    with colf2:
                        selected_time = st.time_input("⏰ Filter by Time (optional)", key="hist_time", value=None)

                    if selected_date:
                        df_hist = df_hist[df_hist["parsed_time"].dt.date == selected_date]
                    if selected_time:
                        df_hist = df_hist[df_hist["parsed_time"].dt.strftime("%H:%M") == selected_time.strftime("%H:%M")]

                    grouped = df_hist.groupby("timestamp_group")

                    for group_time, group_df in grouped:
                        with st.expander(f"🕒 {group_time}", expanded=False):
                            for _, row in group_df.iterrows():
                                st.markdown(f"- **{row['parameter_name']}** — `{row['protocol_use_for_analysis']}`")

                            if st.button(f"📊 View Table - {group_time}", key=f"view_table_{group_time}"):
                                st.session_state.selected_group_data = group_df[[
                                    "parameter_name", "unit", "protocol_use_for_analysis", "result"
                                ]].rename(columns={
                                    "parameter_name": "Name",
                                    "unit": "Unit",
                                    "protocol_use_for_analysis": "Protocol",
                                    "result": "Result"
                                }).to_dict(orient="records")

                if st.session_state.selected_group_data:
                    st.markdown("### 📊 Selected Group Table")
                    df_group = pd.DataFrame(st.session_state.selected_group_data)
                    st.dataframe(df_group)

                    def to_excel(df):
                        output = BytesIO()
                        # Min/Max already excluded from this group table
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False)
                        return output.getvalue()

                    excel_group_data = to_excel(df_group)
                    st.download_button("📥 Download Group", data=excel_group_data, file_name="group_result.xlsx")

        except requests.exceptions.HTTPError as errh:
            st.error(f"❌ Server error: {errh}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection failed. Please check your network.")
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
