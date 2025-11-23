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
     get_top_recent_updates, display_resource_usage,
     list_datasets_by_source
)

# ------------------- DATABASE -------------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DB_FILE = os.path.join(DATA_DIR, "intelligence_platform.db")

conn = connect_database(DB_FILE)
create_all_tables(conn)

load_all_csv_data(conn, os.path.join(DATA_DIR, "cyber_incidents.csv"), "cyber_incidents")
load_all_csv_data(conn, os.path.join(DATA_DIR, "it_tickets.csv"), "it_tickets")
load_all_csv_data(conn, os.path.join(DATA_DIR, "datasets_metadata.csv"), "datasets_metadata")

def cyber_incidents_func():
    
    def view_records():
        incidents = get_all_incidents(conn) 
        st.subheader("Cybersecurity Incidents")
        st.dataframe(incidents, use_container_width=True)
    
    def add_new_incident():
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
                # Insert into database
                insert_incident(conn, str(date), incident_type, severity, status, description, reported_by)
                st.success("✓ Incident added successfully!")
                st.rerun() # Refresh the page to show new incident

    # Example: Update/Delete could be similar
    st.text("Update/Delete forms here")
    
    def delete_cyber_incident():
        # Fetch all incidents
        incidents = get_all_incidents(conn)
        if incidents.empty:
            st.info("No incidents available to delete.")
            return

        # Map incidents to display string (id + type) for selection
        incident_options = [f"{row['id']}: {row['incident_type']}" for idx, row in incidents.iterrows()]

        # Select incident to delete
        selected = st.selectbox("Select incident to delete", incident_options)
        incident_id = int(selected.split(":")[0])  # Extract id

        # Confirmation
        st.warning(f"Are you sure you want to delete incident {incident_id}?")

        if st.button("Delete"):
            # Call your SQL function
            deleted_count = delete_incident(conn, incident_id)
            if deleted_count > 0:
                st.success(f"Incident {incident_id} deleted successfully!")
                st.rerun()
            else:
                st.error(f"Failed to delete incident {incident_id}.")
        

    def data_visualization():
        pass

def cyber_incidents_func():
    
    def view_records():
        tickets = get_all_tickets(conn) 
        st.subheader("IT Tickets")
        st.dataframe(tickets, use_container_width=True)
    
    def add_new_ticket():
        st.subheader("Add New IT Ticket")

        with st.form("add_ticket"):
            ticket_id = st.text_input("Ticket ID")
            priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            category = st.text_input("Category", ["Hardware", "Software", "Network"])
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            created_date = st.date_input("Created Date")
            resolved_date = st.date_input("Resolved Date", value=None)
            assigned_to = st.text_input("Assigned To")

            submitted = st.form_submit_button("Add Ticket")
            if submitted:
                # Insert into database
                insert_ticket(conn, ticket_id, priority, status, category, subject, description,
                               str(created_date), str(resolved_date), assigned_to
                               )
                st.success("✓ Ticket added successfully!")
                st.rerun()  # Refresh page to show new ticket

    
    def delete_cyber_incident():
        # Fetch all incidents
        incidents = get_all_incidents(conn)
        if incidents.empty:
            st.info("No incidents available to delete.")
            return

        # Map incidents to display string (id + type) for selection
        incident_options = [f"{row['id']}: {row['incident_type']}" for idx, row in incidents.iterrows()]

        # Select incident to delete
        selected = st.selectbox("Select incident to delete", incident_options)
        incident_id = int(selected.split(":")[0])  # Extract id

        # Confirmation
        st.warning(f"Are you sure you want to delete incident {incident_id}?")

        if st.button("Delete"):
            # Call your SQL function
            deleted_count = delete_incident(conn, incident_id)
            if deleted_count > 0:
                st.success(f"Incident {incident_id} deleted successfully!")
                st.rerun()
            else:
                st.error(f"Failed to delete incident {incident_id}.")
        


    def data_visualization():
        pass

def datasets_metadata_func():
    
    def view_records():
        datasets = get_all_datasets(conn) 
        st.subheader("Data Science")
        st.dataframe(datasets, use_container_width=True)
    
    def add_new_ticket():
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
                # Insert into database
                insert_incident(conn, str(date), incident_type, severity, status, description, reported_by)
                st.success("✓ Incident added successfully!")
                st.rerun() # Refresh the page to show new incident
    
    def delete_it_ticket():

        """
        Delete an IT ticket via Streamlit UI.
        """
        # Fetch all tickets
        tickets = get_all_tickets(conn)  # Should return a DataFrame
        if tickets.empty:
            st.info("No tickets available to delete.")
            return

        # Map tickets to display string (ticket_id + subject)
        ticket_options = [f"{row['ticket_id']}: {row['subject']}" for idx, row in tickets.iterrows()]

        # Select ticket to delete
        selected = st.selectbox("Select ticket to delete", ticket_options)
        ticket_id = selected.split(":")[0]  # Extract ticket_id

        # Confirmation checkbox
        confirm = st.checkbox(f"Confirm delete ticket {ticket_id}")
        
        if confirm and st.button("Delete Ticket"):
            # Call your SQL function
            deleted_count = delete_ticket(conn, ticket_id)
            if deleted_count > 0:
                st.success(f"Ticket {ticket_id} deleted successfully!")
                st.rerun()  # Refresh page
            else:
                st.error(f"Failed to delete ticket {ticket_id}.")

            

    def data_visualization():
        pass