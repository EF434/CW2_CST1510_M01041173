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
    import streamlit as st
    import pandas as pd

    # Fetch data from DB and store in session_state for mutable operations
    if table_name == "cyber_incidents":
        if "cyber_incidents" not in st.session_state:
            st.session_state.cyber_incidents = get_all_incidents(conn).to_dict("records")
        records = st.session_state.cyber_incidents
        key_column = "id"
    elif table_name == "it_tickets":
        if "it_tickets" not in st.session_state:
            st.session_state.it_tickets = get_all_tickets(conn).to_dict("records")
        records = st.session_state.it_tickets
        key_column = "ticket_id"
    elif table_name == "datasets_metadata":
        if "datasets_metadata" not in st.session_state:
            st.session_state.datasets_metadata = get_all_datasets(conn).to_dict("records")
        records = st.session_state.datasets_metadata
        key_column = "dataset_name"
    else:
        st.error("Unknown table")
        return

    if not records:
        st.info("No records to update/delete")
        return

    # --- DELETE FLOW ---
    names = [str(r[key_column]) for r in records]
    to_delete = st.selectbox("Select record to delete", names)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.warning(f"Are you sure you want to delete '{to_delete}'?")
    with col2:
        if st.button("Delete", key=f"delete_{table_name}", type="primary"):
            idx = names.index(to_delete)
            # Call DB delete function
            if table_name == "cyber_incidents":
                delete_incident(conn, to_delete)
            elif table_name == "it_tickets":
                delete_ticket(conn, to_delete)
            elif table_name == "datasets_metadata":
                delete_dataset(conn, to_delete)
            # Remove from session_state
            records.pop(idx)
            st.success(f"Record '{to_delete}' deleted!")
            st.rerun()

    # --- UPDATE FLOW ---
    selected = st.selectbox("Select record to update", names, key=f"update_{table_name}")
    idx = names.index(selected)
    record = records[idx]

    st.write(f"### Update Record: {selected}")
    with st.form(f"update_form_{table_name}"):
        updated_values = {}
        for col, val in record.items():
            if col == key_column:
                st.text_input(col, val, disabled=True)
                updated_values[col] = val
            elif isinstance(val, int) or isinstance(val, float):
                updated_values[col] = st.number_input(col, value=val)
            else:
                updated_values[col] = st.text_input(col, val)

        if st.form_submit_button("Update"):
            # Update DB using existing functions if applicable
            if table_name == "cyber_incidents":
                update_incident_status(conn, record[key_column], updated_values.get("status", record.get("status")))
            elif table_name == "it_tickets":
                update_ticket(conn, record[key_column], updated_values.get("status", record.get("status")))
            elif table_name == "datasets_metadata":
                update_dataset(conn, record[key_column], updated_values.get("category", record.get("category")))

            # Update session_state
            st.session_state[table_name][idx] = updated_values
            st.success(f"Record '{selected}' updated successfully!")
            st.rerun()


# ------------------- DATA VISUALIZATION -------------------
def data_visualization(conn, table_name):
    st.text(f"Charts / Insights for {table_name} will be implemented here")
