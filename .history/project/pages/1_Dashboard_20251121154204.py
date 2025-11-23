import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
import sys
import os

# Add project root to Python path
sys.path.append(r"C:\CST1510\CW2_CST1510_M01041173")

from app.data.db import connect_database, load_all_csv_data
from app.data.incidents import insert_incident, get_all_incidents

# ----------------------------
# Database & CSV paths
# ----------------------------
db_path = r"C:\CST1510\CW2_CST1510_M01041173\DATA\intelligence_platform.db"
csv_path = r"C:\CST1510\CW2_CST1510_M01041173\DATA\cyber_incidents.csv"
table_name = "cyber_incidents"

# Connect to database
conn = connect_database(db_path)

# ----------------------------
# Load CSV if table is empty
# ----------------------------
incidents_df = get_all_incidents(conn)
if incidents_df.empty:
    rows_loaded = load_all_csv_data(conn, csv_path, table_name)
    st.info(f"✅ {rows_loaded} rows loaded from CSV into the database.")
    incidents_df = get_all_incidents(conn)  # Reload after CSV import

# ----------------------------
# Display existing incidents
# ----------------------------
st.subheader("📋 Current Cyber Incidents")
if not incidents_df.empty:
    # Format date
    if "date" in incidents_df.columns:
        incidents_df["date"] = pd.to_datetime(incidents_df["date"]).dt.date
    
    st.dataframe(
        incidents_df.style
        .background_gradient(subset=['severity'], cmap='Oranges')
        .highlight_max(subset=['severity'], color='red'),
        use_container_width=True
    )
else:
    st.info("No incidents found in the database.")

# ----------------------------
# Add a new incident
# ----------------------------
st.subheader("➕ Add a New Incident")
with st.form("incident_form"):
    date_input = st.date_input("Incident Date", date.today())
    incident_type = st.text_input("Incident Type", placeholder="e.g., Phishing, Malware, DDoS, Ransomware")
    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
    description = st.text_area("Incident Description")
    reported_by = st.text_input("Reported By (Username)")

    submitted = st.form_submit_button("Add Incident")
    if submitted:
        if not incident_type.strip():
            st.error("Incident Type cannot be empty!")
        elif not reported_by.strip():
            st.error("Reported By cannot be empty!")
        else:
            row_id = insert_incident(
                conn,
                date_input.strftime("%Y-%m-%d"),
                incident_type.strip(),
                severity,
                status,
                description.strip(),
                reported_by.strip()
            )
            if row_id:
                st.success(f"Incident #{row_id} added successfully!")

                # Refresh table after adding
                incidents_df = get_all_incidents(conn)
                if "date" in incidents_df.columns:
                    incidents_df["date"] = pd.to_datetime(incidents_df["date"]).dt.date
                st.dataframe(
                    incidents_df.style
                    .background_gradient(subset=['severity'], cmap='Oranges')
                    .highlight_max(subset=['severity'], color='red'),
                    use_container_width=True
                )
            else:
                st.error("❌ Failed to add incident. Check DB connection and table structure.")
