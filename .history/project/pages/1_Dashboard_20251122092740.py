import streamlit as st
import pandas as pd
from datetime import date

import sys, os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

# ------------ IMPORT MODULES ------------
from app.data.db import connect_database, load_all_csv_data
from app.data.schema import create_all_tables

# Cybersecurity functions
from app.data.incidents import (
    get_all_incidents, insert_incident, update_incident_status, delete_incident,
    get_incidents_by_type_count, get_high_severity_by_status
)

# IT Operations functions
from app.data.tickets import (
    insert_ticket, update_ticket, delete_ticket, get_unresolved_tickets, get_ticket_delays
)

# Data Science functions
from app.data.datasets import (
    insert_dataset, update_dataset, delete_dataset,
    get_top_recent_updates, display_resource_usage, list_datasets_by_source
)

# Utils
from project.utils  import view_records, add_new_record, update_delete_record

# ------------ DATABASE SETUP ------------
DB_FILE = os.path.join(BASE_DIR, "DATA", "intelligence_platform.db")
conn = connect_database(DB_FILE)
create_all_tables(conn)

# ------------ LOAD CSV DATA INTO DATABASE ------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")

# Cyber incidents
load_all_csv_data(conn,
                  csv_path=os.path.join(DATA_DIR, "cyber_incidents.csv"),
                  table_name="cyber_incidents")

# IT tickets
load_all_csv_data(conn,
                  csv_path=os.path.join(DATA_DIR, "it_tickets.csv"),
                  table_name="it_tickets")

# Datasets
load_all_csv_data(conn,
                  csv_path=os.path.join(DATA_DIR, "datasets_metadata.csv"),
                  table_name="datasets_metadata")

# ---------- Session state ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# ------------ STREAMLIT CONFIG ------------
st.set_page_config(page_title="Dashboard", layout="wide", )
st.markdown(
    """
    <h1 style='text-align: center; color: #1f77b4; font-family: "Segoe UI", sans-serif;'>
         Multi-Domain Intelligence Platform
    </h1>
    """,
    unsafe_allow_html=True
)

# ------------ DATABASE SETUP ------------
DB_FILE = os.path.join(BASE_DIR, "DATA", "intelligence_platform.db")
conn = connect_database(DB_FILE)
create_all_tables(conn)

domain_choice = st.sidebar.selectbox("Select Domain", list(domains.keys()))
domain_data = domains[domain_choice]

# Action choices
domain_choice = st.sidebar.selectbox("Select Domain", ["Cybersecurity", "IT Operations", "Data Science"])
actions = st.sidebar.multiselect(
    "Select Actions",
    ["📄 View Records", "➕ Add New Record", "✏ Update / Delete", "📊 Charts / Insights"],
    default=["📄 View Records"]
)


# ------------------- LOAD DATA -------------------
if "df" not in st.session_state or st.session_state.get("domain") != domain_choice:
    if domain_choice == "Cybersecurity":
        st.session_state.df = get_all_incidents(conn)
    elif domain_choice == "IT Operations":
        st.session_state.df = get_unresolved_tickets(conn)
    elif domain_choice == "Data Science":
        st.session_state.df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
    st.session_state.domain = domain_choice

df = st.session_state.df

# Helper function to refresh dataframe
def refresh_data():
    if domain_choice == "Cybersecurity":
        st.session_state.df = get_all_incidents(conn)
    elif domain_choice == "IT Operations":
        st.session_state.df = get_unresolved_tickets(conn)
    elif domain_choice == "Data Science":
        st.session_state.df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)

# ------------------- ACTIONS -------------------
for action in actions:
    # ------------------- VIEW RECORDS -------------------
    if action == "📄 View Records":
        filters = {}
        if not df.empty:
            if domain_choice == "Cybersecurity":
                filters = {"severity": df["severity"].unique(), "status": df["status"].unique()}
            elif domain_choice == "IT Operations":
                filters = {"priority": df["priority"].unique(), "status": df["status"].unique()}
        view_records(domain_choice, df, filters)

    # ------------------- ADD NEW RECORD -------------------
    elif action == "➕ Add New Record":
        if domain_choice == "Cybersecurity":
            add_new_record(
                "Cybersecurity",
                insert_func=lambda **kwargs: insert_incident(conn, **kwargs),
                form_fields=[
                    {"label": "Incident Date", "type": "date"},
                    {"label": "Incident Type", "type": "text"},
                    {"label": "Severity", "type": "select", "options": ["Low", "Medium", "High", "Critical"]},
                    {"label": "Status", "type": "select", "options": ["Open", "Investigating", "Resolved", "Closed"]},
                    {"label": "Description", "type": "textarea"},
                    {"label": "Reported By", "type": "text"}
                ]
            )
        elif domain_choice == "IT Operations":
            add_new_record(
                "IT Operations",
                insert_func=lambda **kwargs: insert_ticket(conn, **kwargs),
                form_fields=[
                    {"label": "Ticket ID", "type": "text"},
                    {"label": "Priority", "type": "select", "options": ["Low", "Medium", "High", "Critical"]},
                    {"label": "Status", "type": "select", "options": ["Open", "In Progress", "Resolved", "Closed"]},
                    {"label": "Category", "type": "text"},
                    {"label": "Subject", "type": "text"},
                    {"label": "Description", "type": "textarea"},
                    {"label": "Created Date", "type": "date"},
                    {"label": "Resolved Date", "type": "date"},
                    {"label": "Assigned To", "type": "text"}
                ]
            )
        elif domain_choice == "Data Science":
            add_new_record(
                "Data Science",
                insert_func=lambda **kwargs: insert_dataset(conn, **kwargs),
                form_fields=[
                    {"label": "Dataset Name", "type": "text"},
                    {"label": "Source", "type": "text"},
                    {"label": "Category", "type": "text"},
                    {"label": "Last Updated", "type": "date"},
                    {"label": "Record Count", "type": "text"},
                    {"label": "File Size (MB)", "type": "text"}
                ]
            )
        refresh_data()

    # ------------------- UPDATE / DELETE -------------------
    elif action == "✏ Update / Delete":
        if domain_choice == "Cybersecurity":
            update_delete_record(
                "Cybersecurity", df,
                update_func=lambda id, **kwargs: update_incident_status(conn, id, **kwargs),
                delete_func=lambda id: delete_incident(conn, id),
                update_fields=[
                    {"label": "Incident Date", "type": "date"},
                    {"label": "Incident Type", "type": "text"},
                    {"label": "Severity", "type": "select", "options": ["Low", "Medium", "High", "Critical"]},
                    {"label": "Status", "type": "select", "options": ["Open", "Investigating", "Resolved", "Closed"]},
                    {"label": "Description", "type": "textarea"},
                    {"label": "Reported By", "type": "text"}
                ]
            )
        elif domain_choice == "IT Operations":
            update_delete_record(
                "IT Operations", df,
                update_func=lambda id, **kwargs: update_ticket(conn, id, **kwargs),
                delete_func=lambda id: delete_ticket(conn, id),
                update_fields=[
                    {"label": "Ticket ID", "type": "text"},
                    {"label": "Priority", "type": "select", "options": ["Low", "Medium", "High", "Critical"]},
                    {"label": "Status", "type": "select", "options": ["Open", "In Progress", "Resolved", "Closed"]},
                    {"label": "Category", "type": "text"},
                    {"label": "Subject", "type": "text"},
                    {"label": "Description", "type": "textarea"},
                    {"label": "Created Date", "type": "date"},
                    {"label": "Resolved Date", "type": "date"},
                    {"label": "Assigned To", "type": "text"}
                ]
            )
        elif domain_choice == "Data Science":
            update_delete_record(
                "Data Science", df,
                update_func=lambda id, **kwargs: update_dataset(conn, id, **kwargs),
                delete_func=lambda id: delete_dataset(conn, id),
                update_fields=[
                    {"label": "Dataset Name", "type": "text"},
                    {"label": "Source", "type": "text"},
                    {"label": "Category", "type": "text"},
                    {"label": "Last Updated", "type": "date"},
                    {"label": "Record Count", "type": "text"},
                    {"label": "File Size (MB)", "type": "text"}
                ]
            )
        refresh_data()

    # ------------------- CHARTS / INSIGHTS -------------------
    elif action == "📊 Charts / Insights":
        st.subheader(f"📊 {domain_choice} Analytics")
        if df.empty:
            st.info("No data available for charts.")
        else:
            if domain_choice == "Cybersecurity":
                for chart in [get_incidents_by_type_count, get_high_severity_by_status]:
                    st.write(f"📌 {chart.__name__}")
                    st.dataframe(chart(conn), use_container_width=True)
            elif domain_choice == "IT Operations":
                for chart in [get_ticket_delays]:
                    st.write(f"📌 {chart.__name__}")
                    st.dataframe(chart(conn), use_container_width=True)
            elif domain_choice == "Data Science":
                for chart in [get_top_recent_updates, display_resource_usage, list_datasets_by_source]:
                    st.write(f"📌 {chart.__name__}")
                    st.dataframe(chart(conn), use_container_width=True)