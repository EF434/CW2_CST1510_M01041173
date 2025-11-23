import sys, os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

import streamlit as st
import pandas as pd
from datetime import date

# ------------ IMPORT MODULES ------------
from app.data.db import connect_database, load_all_csv_data
from app.data.schema import create_all_tables
from app.data.incidents import (
    get_all_incidents, 
    insert_incident, 
    update_incident_status,
    delete_incident,
    get_incidents_by_type_count,
    get_high_severity_by_status
)

# ------------ STREAMLIT CONFIG ------------
st.set_page_config(page_title="Intelligence Platform", layout="wide")
st.title("🛡 Cyber Intelligence Platform")

# ------------ DATABASE SETUP ------------
DB_FILE = os.path.join(BASE_DIR, "DATA", "intelligence_platform.db")
CSV_FILE = os.path.join(BASE_DIR, "DATA", "cyber_incidents.csv")

conn = connect_database(DB_FILE)
create_all_tables(conn)

# ------------ INITIALIZE SESSION STATE DATAFRAME ------------
if "df" not in st.session_state:
    df = get_all_incidents(conn)
    if df.empty:
        st.warning("⚠ No incident data found in the database. Loading data from CSV...")
        rows = load_all_csv_data(conn, CSV_FILE, "cyber_incidents")
        df = get_all_incidents(conn)
        st.success(f"📥 Imported {rows} records from CSV!")
    st.session_state.df = df

# Helper function to refresh dataframe
def refresh_data():
    st.session_state.df = get_all_incidents(conn)

df = st.session_state.df

# ------------ SIDEBAR NAVIGATION ------------
actions = st.sidebar.multiselect(
options = ["📄 View Records", "➕ Add New Record", "✏ Update / Delete", "📊 Charts / Insights"]

)

# =====================================================================
# 📄 VIEW INCIDENT RECORDS
# =====================================================================
if action == "📄 View Records":
    st.subheader("📄 All Cybersecurity Incidents")
    if not df.empty:
        with st.expander("🔍 Filters"):
            severity_filter = st.multiselect("Severity", df["severity"].unique(), df["severity"].unique())
            status_filter = st.multiselect("Status", df["status"].unique(), df["status"].unique())
        filtered = df[(df["severity"].isin(severity_filter)) & (df["status"].isin(status_filter))]
        st.caption(f"Showing {len(filtered)} filtered records")
        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("No data available.")

# =====================================================================
# ➕ ADD NEW INCIDENT
# =====================================================================
elif action == "➕ Add New Record":
    st.subheader("➕ Add a New Cyber Incident")
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            incident_date = st.date_input("Incident Date", value=date.today())
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        with col2:
            incident_type = st.selectbox("Incident Type", [
                "Phishing", "Malware", "DDoS", "Insider Attack", "Ransomware", "Other"
            ])
            status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
        description = st.text_area("Description")
        reporter = st.text_input("Reported By (optional)")
        submit = st.form_submit_button("Save Incident")

    if submit:
        insert_incident(
            conn,
            str(incident_date),
            incident_type,
            severity,
            status,
            description,
            reporter if reporter else None
        )
        st.success("✔ Incident added successfully!")
        refresh_data()  # update dataframe in session state

# =====================================================================
# ✏ UPDATE OR DELETE INCIDENT
# =====================================================================
elif action == "✏ Update / Delete":
    st.subheader("✏ Update or Delete an Incident")
    if df.empty:
        st.warning("No records available.")
    else:
        selected_id = st.selectbox("Select Incident ID:", df["id"])
        selected_row = df[df["id"] == selected_id].iloc[0]
        st.write("📌 Existing Record:")
        st.json(selected_row.to_dict())

        new_status = st.selectbox("Update Status:", ["Open", "Investigating", "Resolved", "Closed"], index=0)

        if st.button("Update Status"):
            update_incident_status(conn, selected_id, new_status)
            st.success("Status Updated Successfully!")
            refresh_data()  # update dataframe

        if st.button("❌ Delete Incident"):
            delete_incident(conn, selected_id)
            st.error("Record Deleted!")
            refresh_data()  # update dataframe

# =====================================================================
# 📊 INSIGHTS & CHARTS
# =====================================================================
elif action == "📊 Charts / Insights":
    if df.empty:
        st.info("No data available for charts.")
    else:
        st.subheader("📊 Cyber Incident Analytics")
        col1, col2 = st.columns(2)
        with col1:
            st.write("📌 Incidents by Type")
            type_data = get_incidents_by_type_count(conn)
            st.bar_chart(type_data.set_index("incident_type"))
        with col2:
            st.write("🚨 High Severity Status Breakdown")
            severity_data = get_high_severity_by_status(conn)
            st.area_chart(severity_data.set_index("status"))
        st.write("📄 Full Dataset")
        st.dataframe(df)
