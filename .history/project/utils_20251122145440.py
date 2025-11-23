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

# Config & Utils
from config.add_config import ADD_CONFIG
from project.utils import view_records, add_new_record, update_delete_record

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
def view_records(domain_name, df, filters=None):
    st.subheader(f"📄 {domain_name} Records")
    if df.empty:
        st.info("No data available.")
        return

    if filters:
        with st.expander("🔍 Filters"):
            selected_filters = {}
            for col, options in filters.items():
                selected_filters[col] = st.multiselect(col, options, default=options)
            for col, selected in selected_filters.items():
                df = df[df[col].isin(selected)]
    
    st.caption(f"Showing {len(df)} filtered records")
    st.dataframe(df, use_container_width=True)


# ----------------- ADD NEW RECORD -----------------
def add_new_record(domain_name, insert_func, form_fields):
    st.subheader(f"➕ Add New {domain_name} Record")
    with st.form(f"add_form_{domain_name}"):
        title = st.text_input("Incident Title")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        description = st.text_area("Description")
        reported_by = st.text_input("Reported By (optional)")

        submitted = st.form_submit_button("Add Incident")


        if st.form_submit_button("Save Record"):
            insert_incident(conn, title, severity, status, description, reported_by)
            #session state
            st.success(f"✔ {domain_name} record added successfully!")


# ----------------- UPDATE / DELETE -----------------
def update_delete_record(domain_name, df, update_func=None, delete_func=None, update_fields=None):
    st.subheader(f"✏ Update / Delete {domain_name} Record")
    
    if df.empty:
        st.warning("No records available.")
        return

    # Select record to delete
    record_names = [f"{r['id']} - {r['title']}" for _, r in df.iterrows()]  # display ID + title
    to_delete = st.selectbox("Select record to delete", record_names)

    # Confirmation columns
    col1, col2 = st.columns([3, 1])
    with col1:
        st.warning(f"Delete {to_delete}?")
    with col2:
        if st.button("Delete", key="delete_button"):
            # Extract ID from the string
            record_id = int(to_delete.split(" - ")[0])
            if delete_func:
                delete_func(record_id)  # Call your SQL delete function
                st.success(f"Record {record_id} deleted successfully!")
                st.experimental_rerun()  # Refresh to reflect changes
