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

# Domain-specific modules
from app.data.incidents import (
    get_all_incidents, insert_incident, update_incident_status, delete_incident
)
from app.data.tickets import (
    get_unresolved_tickets, insert_ticket, update_ticket, delete_ticket
)
from app.data.datasets import (
    list_datasets_by_source, insert_dataset, update_dataset, delete_dataset
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

# ----------------- DOMAIN CONFIG -----------------
DOMAINS = {
    "Cybersecurity": {
        "table": "cyber_incidents",
        "get_all": get_all_incidents,
        "insert": insert_incident,
        "update": update_incident_status,
        "delete": delete_incident,
        "fields": ["title", "severity", "status", "description", "reported_by"]
    },
    "IT Operations": {
        "table": "it_tickets",
        "get_all": get_unresolved_tickets,
        "insert": insert_ticket,
        "update": update_ticket,
        "delete": delete_ticket,
        "fields": ["title", "priority", "status", "assigned_to"]
    },
    "Data Science": {
        "table": "datasets_metadata",
        "get_all": list_datasets_by_source,
        "insert": insert_dataset,
        "update": update_dataset,
        "delete": delete_dataset,
        "fields": ["dataset_name", "source", "last_updated", "size"]
    }
}

# ----------------- GENERIC FUNCTIONS -----------------
def view_records(domain_name):
    config = DOMAINS[domain_name]
    df = pd.DataFrame(config["get_all"](conn))
    st.subheader(f"📄 {domain_name} Records")

    if df.empty:
        st.info("No data available.")
        return

    # Custom filtering
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


def add_new_record(domain_name):
    config = DOMAINS[domain_name]
    st.subheader(f"➕ {domain_name} - Add New Record")
    
    with st.form(f"add_form_{domain_name}"):
        inputs = {}
        for field in config["fields"]:
            if field in ["severity", "status", "priority"]:  # Example selectbox fields
                options = ["Low", "Medium", "High", "Critical"] if field == "severity" else ["Open", "In Progress", "Resolved"]
                inputs[field] = st.selectbox(field.title(), options)
            else:
                inputs[field] = st.text_input(field.title())

        if st.form_submit_button("Save Record"):
            config["insert"](conn, **inputs)
            st.success(f"{domain_name} record added successfully!")


def update_delete_record(domain_name, df):
    config = DOMAINS[domain_name]
    st.subheader(f"✏ Update / Delete {domain_name} Record")
    
    if df.empty:
        st.warning("No records available.")
        return

    selected_id = st.selectbox("Select Record ID", df["id"])
    selected_row = df[df["id"] == selected_id].iloc[0]
    st.json(selected_row.to_dict())

    # Update
    updated_values = {}
    for field in config["fields"]:
        updated_values[field] = st.text_input(f"Update {field}", value=selected_row.get(field, ""))
    
    if st.button("Update Record"):
        config["update"](conn, selected_id, **updated_values)
        st.success("Record Updated Successfully!")

    # Delete
    if st.button("❌ Delete Record"):
        config["delete"](conn, selected_id)
        st.error("Record Deleted!")
