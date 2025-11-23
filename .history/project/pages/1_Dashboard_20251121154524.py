import streamlit as st
import pandas as pd
from pathlib import Path
from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident

# ----------------------------
# Database connection
# ----------------------------
conn = connect_database(r"C:\CST1510\CW2_CST1510_M01041173\DATA\intelligence_platform.db")

# ----------------------------
# Page title
# ----------------------------
st.title("Cyber Incidents Dashboard")

# ----------------------------
# READ: Display incidents from database
# ----------------------------
incidents = get_all_incidents(conn)

if not incidents.empty:
    # Format date if column exists
    if "date" in incidents.columns:
        incidents["date"] = pd.to_datetime(incidents["date"]).dt.date

    # Highlight High/Critical severity
    def highlight_severity(val):
        color = 'red' if val in ['High', 'Critical'] else ''
        return f'background-color: {color}'

    st.subheader("📋 Current Cyber Incidents")
    st.dataframe(
        incidents.style.applymap(highlight_severity, subset=['severity']),
        use_container_width=True
    )
else:
    st.info("No incidents found in the database.")

# ----------------------------
# CREATE: Add new incident
# ----------------------------
st.subheader("➕ Add a New Incident")
with st.form("new_incident_form"):
    title = st.text_input("Incident Title")
    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
    
    submitted = st.form_submit_button("Add Incident")
    if submitted:
        if not title.strip():
            st.error("Incident title cannot be empty!")
        else:
            insert_incident(conn, title.strip(), severity, status)
            st.success("✓ Incident added successfully!")
            st.experimental_rerun()  # Refresh page to show new incident

# ----------------------------
# Initialize session records
# ----------------------------
if "records" not in st.session_state:
    st.session_state.records = []

# ----------------------------
# Add record form
# ----------------------------
st.subheader("➕ Add Session Record")
with st.form("add_record_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["User", "Admin"])
    
    if st.form_submit_button("Add Record"):
        record = {"name": name, "email": email, "role": role}
        st.session_state.records.append(record)
        st.success("Record added!")

# ----------------------------
# Display all session records
# ----------------------------
if st.session_state.records:
    st.subheader("All Records")
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No session records found.")

# ----------------------------
# Update record
# ----------------------------
if st.session_state.records:
    names = [r["name"] for r in st.session_state.records]
    selected = st.selectbox("Select record to update", names)
    idx = names.index(selected)
    record = st.session_state.records[idx]

    with st.form("update_record_form"):
        new_email = st.text_input("Email", record["email"])
        new_role = st.selectbox("Role", ["User", "Admin"], index=0 if record["role"]=="User" else 1)
        if st.form_submit_button("Update Record"):
            st.session_state.records[idx]["email"] = new_email
            st.session_state.records[idx]["role"] = new_role
            st.success("Record updated!")

# ----------------------------
# Delete record
# ----------------------------
if st.session_state.records:
    names = [r["name"] for r in st.session_state.records]
    to_delete = st.selectbox("Select record to delete", names)
    
    col1, col2 = st.columns([3,1])
    with col1:
        st.warning(f"Delete {to_delete}?")
    with col2:
        if st.button("Delete", key="delete_button"):
            idx = names.index(to_delete)
            st.session_state.records.pop(idx)
            st.success("Record deleted!")
            st.experimental_rerun()

# ----------------------------
# Security metrics
# ----------------------------
st.subheader("📊 Security Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Threats Detected", 247, delta="+12")
col2.metric("Vulnerabilities", 8, delta="-3")
col3.metric("Incidents", 3, delta="+1")

# ----------------------------
# Threat distribution
# ----------------------------
st.subheader("Threat Distribution")
threat_data = {"Malware": 89, "Phishing": 67, "DDoS": 45, "Intrusion": 46}
st.bar_chart(pd.DataFrame.from_dict(threat_data, orient='index', columns=['Count']))
