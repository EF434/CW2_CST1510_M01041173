# ------------------- IMPORTS -------------------
import streamlit as st
import pandas as pd
import sys
import os

# Path setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

# ------------ APP MODULES ------------
from app.data.db import connect_database, load_all_csv_data
from app.data.schema import create_all_tables

# Domain: Cybersecurity
from app.data.incidents import (
    get_all_incidents, insert_incident, update_incident_status, delete_incident,
    get_incidents_by_type_count, get_high_severity_by_status
)

# Domain: IT Operations
from app.data.tickets import (
    insert_ticket, update_ticket, delete_ticket, get_unresolved_tickets, get_ticket_delays
)

# Domain: Data Science
from app.data.datasets import (
    insert_dataset, update_dataset, delete_dataset,
    get_top_recent_updates, display_resource_usage, list_datasets_by_source
)



# ------------------- DATABASE SETUP -------------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DB_FILE = os.path.join(DATA_DIR, "intelligence_platform.db")

conn = connect_database(DB_FILE)
create_all_tables(conn)

# Load CSVs only if DB is empty
load_all_csv_data(conn, os.path.join(DATA_DIR, "cyber_incidents.csv"), "cyber_incidents")
load_all_csv_data(conn, os.path.join(DATA_DIR, "it_tickets.csv"), "it_tickets")
load_all_csv_data(conn, os.path.join(DATA_DIR, "datasets_metadata.csv"), "datasets_metadata")

# ----------------- VIEW RECORDS -----------------
def view_records(domain_name, df):
    st.subheader(f"📄 {domain_name} Records")
    if df.empty:
        st.info("No data available.")
        return

    # ------------------- Custom User Filtering -------------------
    st.markdown("### Filters")
    st.info("Enter exact column name and value. Column names must match exactly!")

    df_filtered = df.copy()
    custom_col = st.text_input("Enter exact column name to filter")
    custom_val = st.text_input("Enter value to filter (exact match)")

    if custom_col or custom_val:
        if custom_col not in df.columns:
            st.warning(f"Column '{custom_col}' not found in this domain. Please enter an exact column name.")
        elif custom_val:
            df_filtered = df_filtered[df_filtered[custom_col] == custom_val]

    st.caption(f"Showing {len(df_filtered)} filtered records")
    st.dataframe(df_filtered, use_container_width=True)



# ----------------- ADD NEW RECORD -----------------
def add_new_record(domain_name):
    st.subheader(f"➕ {domain_name} - Add New Record")
    with st.form(f"add_form_{domain_name}"):
        title = st.text_input("Incident Title")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        description = st.text_area("Description")
        reported_by = st.text_input("Reported By (optional)")

        submitted = st.form_submit_button("Add Incident")


        if st.form_submit_button("Save Record"):
            insert_incident(conn, title, severity, status, description, reported_by)
            #session
            st.success(f"✔ {domain_name} record added successfully!")
            st.rerun


# ----------------- UPDATE / DELETE -----------------
def update_delete_record(domain_name, df):
    st.subheader(f"✏ Update / Delete {domain_name} Record")
    if df.empty:
        st.warning("No records available.")
        return

    selected_id = st.selectbox("Select Record ID:", df["id"])
    selected_row = df[df["id"] == selected_id].iloc[0]
    st.json(selected_row.to_dict())

    if update_func and update_fields:
        updated_values = {}
        for field in update_fields:
            label = field["label"]
            options = field.get("options")
            if options:
                updated_values[label] = st.selectbox(f"Update {label}:", options)
            else:
                updated_values[label] = st.text_input(f"Update {label}:", value=selected_row[label])
        if st.button("Update Record"):
            update_func(selected_id, **updated_values)
            st.success("Record Updated Successfully!")

    if delete_func and st.button("❌ Delete Record"):
        delete_func(selected_id)
        st.error("Record Deleted!")
