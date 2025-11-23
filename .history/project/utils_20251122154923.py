# ------------------- IMPORTS -------------------
import streamlit as st
import pandas as pd
import os
import sys

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
os.makedirs(DATA_DIR, exist_ok=True)

conn = connect_database(DB_FILE)
create_all_tables(conn)

# Load CSVs only if DB is empty
load_all_csv_data(conn, os.path.join(DATA_DIR, "cyber_incidents.csv"), "cyber_incidents")
load_all_csv_data(conn, os.path.join(DATA_DIR, "it_tickets.csv"), "it_tickets")
load_all_csv_data(conn, os.path.join(DATA_DIR, "datasets_metadata.csv"), "datasets_metadata")

# ----------------- GENERIC FUNCTIONS -----------------
def view_records(df, domain_name):
    st.subheader(f"📄 {domain_name} Records")
    if df.empty:
        st.info("No data available.")
        return df

    st.markdown("### Filters")
    st.info("Enter exact column name and value. Column names must match exactly!")
    df_filtered = df.copy()
    custom_col = st.text_input("Column Name")
    custom_val = st.text_input("Value")

    if custom_col and custom_val:
        if custom_col not in df.columns:
            st.warning(f"Column '{custom_col}' not found.")
        else:
            df_filtered = df_filtered[df_filtered[custom_col] == custom_val]

    st.caption(f"Showing {len(df_filtered)} records")
    st.dataframe(df_filtered, use_container_width=True)
    return df_filtered


def add_new_record(insert_func, fields, domain_name):
    st.subheader(f"➕ {domain_name} - Add New Record")
    
    with st.form(f"add_form_{domain_name}"):
        inputs = {}
        for field in fields:
            inputs[field] = st.text_input(field.title())
        if st.form_submit_button("Save Record"):
            insert_func(conn, **inputs)
            st.success(f"{domain_name} record added successfully!")


def update_delete_record(update_func, delete_func, df, fields, domain_name):
    st.subheader(f"✏ Update / Delete {domain_name} Record")
    
    if df.empty:
        st.warning("No records available.")
        return

    selected_id = st.selectbox("Select Record ID", df["id"])
    selected_row = df[df["id"] == selected_id].iloc[0]
    st.json(selected_row.to_dict())

    updated_values = {}
    for field in fields:
        updated_values[field] = st.text_input(f"Update {field}", value=selected_row.get(field, ""))
    
    if st.button("Update Record"):
        update_func(conn, selected_id, **updated_values)
        st.success("Record Updated Successfully!")
    if st.button("❌ Delete Record"):
        delete_func(conn, selected_id)
        st.error("Record Deleted!")

# ----------------- STREAMLIT APP -----------------
st.title("Intelligence Platform Dashboard")

domain_choice = st.selectbox(
    "Select Domain",
    ["Cybersecurity", "IT Operations", "Data Science"]
)

if domain_choice == "Cybersecurity":
    df = pd.DataFrame(get_all_incidents(conn))
    df_filtered = view_records(df, "Cybersecurity")
    add_new_record(insert_incident, ["title", "severity", "status", "description", "reported_by"], "Cybersecurity")
    update_delete_record(update_incident_status, delete_incident, df_filtered, ["title", "severity", "status", "description", "reported_by"], "Cybersecurity")

elif domain_choice == "IT Operations":
    df = pd.DataFrame(get_unresolved_tickets(conn))
    df_filtered = view_records(df, "IT Operations")
    add_new_record(insert_ticket, ["title", "priority", "status", "assigned_to"], "IT Operations")
    update_delete_record(update_ticket, delete_ticket, df_filtered, ["title", "priority", "status", "assigned_to"], "IT Operations")

elif domain_choice == "Data Science":
    df = pd.DataFrame(list_datasets_by_source(conn))
    df_filtered = view_records(df, "Data Science")
    add_new_record(insert_dataset, ["dataset_name", "source", "last_updated", "size"], "Data Science")
    update_delete_record(update_dataset, delete_dataset, df_filtered, ["dataset_name", "source", "last_updated", "size"], "Data Science")
