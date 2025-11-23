# ------------------- IMPORTS -------------------
import streamlit as st
import pandas as pd
import sys
import os

# Path setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

# ------------ DB + Modules ------------
from app.data.db import connect_database, load_all_csv_data
from app.data.schema import create_all_tables

# Cybersecurity
from app.data.incidents import (
     insert_incident, get_all_incidents,
    update_incident_status, delete_incident,
    get_incidents_by_type_count, get_high_severity_by_status,
    get_incident_types_with_many_cases, get_incident_trend, unresolved_incidents_by_type,
    resolution_time_by_type
)

# IT Ops
from app.data.tickets import (
    insert_ticket, get_all_tickets,
    update_ticket, delete_ticket,
    get_unresolved_tickets, get_ticket_delays
)

# Data Science
from app.data.datasets import (
     insert_dataset, update_dataset, get_all_datasets,
     list_datasets_by_source, delete_dataset,
     get_top_recent_updates, display_resource_usage
)

# ------------------- DATABASE -------------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DB_FILE = os.path.join(DATA_DIR, "intelligence_platform.db")

conn = connect_database(DB_FILE)
create_all_tables(conn)


# ------------------- VIEW RECORDS -------------------
def view_records(conn, table_name):
    if table_name == "cyber_incidents":
        df = get_all_incidents(conn)
        st.subheader("Cybersecurity Incidents")
    elif table_name == "it_tickets":
        df = get_all_tickets(conn)
        st.subheader("IT Tickets")
    elif table_name == "datasets_metadata":
        df = get_all_datasets(conn)
        st.subheader("Data Science")
    else:
        st.error("Unknown table")
        return
    st.dataframe(df, use_container_width=True)


# ------------------- ADD NEW RECORD -------------------
def add_new_record(conn, table_name):
    if table_name == "cyber_incidents":
        st.subheader("Add New Cybersecurity Incident")
        with st.form("add_incident"):
            date = st.date_input("Date")
            incident_type = st.selectbox("Incident Type", ["Phishing", "Malware", "DDoS", "Ransomware"])
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            description = st.text_area("Description")
            reported_by = st.text_input("Reported by")
            submitted = st.form_submit_button("Add Incident")
            if submitted:
                insert_incident(conn, str(date), incident_type, severity, status, description, reported_by)
                st.success("✓ Incident added successfully!")
                st.rerun()

    elif table_name == "it_tickets":
        st.subheader("Add New IT Ticket")
        with st.form("add_ticket"):
            ticket_id = st.text_input("Ticket ID")
            priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            category = st.text_input("Category")
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            created_date = st.date_input("Created Date")
            resolved_date = st.date_input("Resolved Date", value=pd.NaT)
            assigned_to = st.text_input("Assigned To")
            submitted = st.form_submit_button("Add Ticket")
            if submitted:
                insert_ticket(conn, ticket_id, priority, status, category, subject, description,
                              str(created_date), str(resolved_date), assigned_to)
                st.success("✓ Ticket added successfully!")
                st.rerun()

    elif table_name == "datasets_metadata":
        st.subheader("Add New Dataset Metadata")
        with st.form("add_dataset_form"):
            dataset_name = st.text_input("Dataset Name")
            category = st.selectbox("Category", ["Threat Intelligence", "Network Logs", "User Data", "Other"])
            source = st.text_input("Source / Origin")
            last_updated = st.date_input("Last Updated")
            record_count = st.number_input("Record Count", min_value=0, step=1)
            file_size_mb = st.number_input("File Size (MB)", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Add Dataset")
            if submitted:
                try:
                    insert_dataset(conn, dataset_name, category, source, str(last_updated), record_count, file_size_mb)
                    st.success(f"✓ Dataset '{dataset_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add dataset: {e}")


# ------------------- UPDATE / DELETE -------------------
def update_delete_record(conn, table_name):
  

    # --- Select record to edit/delete ---
    record_ids = df[key_column].tolist()
    selected_id = st.selectbox(f"Select {key_column} to edit/delete", record_ids)
    record = df[df[key_column] == selected_id].iloc[0]

    st.write("### Record Details")
    updated_values = {}

    # --- Form for all fields ---
    with st.form("update_delete_form"):
        for col, val in record.items():
            if col == key_column:
                st.text_input(col, val, disabled=True)
                updated_values[col] = val
            elif pd.api.types.is_numeric_dtype(type(val)) or isinstance(val, int) or isinstance(val, float):
                updated_values[col] = st.number_input(col, value=val)
            else:
                updated_values[col] = st.text_input(col, val)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Update"):
                # --- Dynamically update all columns in the database ---
                columns_to_update = [col for col in updated_values if col != key_column]
                set_clause = ", ".join([f"{col} = ?" for col in columns_to_update])
                values = [updated_values[col] for col in columns_to_update]
                values.append(selected_id)

                table_mapping = {
                    "cyber_incidents": "cyber_incidents",
                    "it_tickets": "it_tickets",
                    "datasets_metadata": "datasets_metadata"
                }

                try:
                    with conn:
                        conn.execute(
                            f"UPDATE {table_mapping[table_name]} SET {set_clause} WHERE {key_column} = ?",
                            values
                        )
                    st.success(f"Record '{selected_id}' updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update record: {e}")

        with col2:
            if st.form_submit_button("Delete", type="primary"):
                # --- Delete record ---
                delete_mapping = {
                    "cyber_incidents": delete_incident,
                    "it_tickets": delete_ticket,
                    "datasets_metadata": delete_dataset
                }
                delete_mapping[table_name](conn, selected_id)
                st.success(f"Record '{selected_id}' deleted!")
                st.rerun()

# ------------------- DATA VISUALIZATION -------------------
def data_visualization(conn, table_name):
    st.text(f"Charts / Insights for {table_name} will be implemented here")
