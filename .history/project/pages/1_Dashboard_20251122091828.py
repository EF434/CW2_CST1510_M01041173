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
st.set_page_config(page_title="Dashb", layout="wide")
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

# ------------ SIDEBAR NAVIGATION ------------
domains = {
    "Cybersecurity": {
        "get_df": lambda: get_all_incidents(conn),
        "insert_func": insert_incident,
        "update_func": update_incident_status,
        "delete_func": delete_incident,
        "charts": [get_incidents_by_type_count, get_high_severity_by_status],
        "fields": [
            {"label": "Incident Date", "type": "date"},
            {"label": "Incident Type", "type": "text"},
            {"label": "Severity", "type": "select", "options": ["Low", "Medium", "High", "Critical"]},
            {"label": "Status", "type": "select", "options": ["Open", "Investigating", "Resolved", "Closed"]},
            {"label": "Description", "type": "textarea"},
            {"label": "Reported By", "type": "text"}
        ]
    },
    "IT Operations": {
        "get_df": lambda: get_unresolved_tickets(conn),
        "insert_func": insert_ticket,
        "update_func": update_ticket,
        "delete_func": delete_ticket,
        "charts": [get_ticket_delays],
        "fields": [
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
    },
    "Data Science": {
        "get_df": lambda: pd.read_sql_query("SELECT * FROM datasets_metadata", conn),
        "insert_func": insert_dataset,
        "update_func": update_dataset,
        "delete_func": delete_dataset,
        "charts": [get_top_recent_updates, display_resource_usage, list_datasets_by_source],
        "fields": [
            {"label": "Dataset Name", "type": "text"},
            {"label": "Source", "type": "text"},
            {"label": "Category", "type": "text"},
            {"label": "Last Updated", "type": "date"},
            {"label": "Record Count", "type": "text"},
            {"label": "File Size (MB)", "type": "text"}
        ]
    }
}

domain_choice = st.sidebar.selectbox("Select Domain", list(domains.keys()))
domain_data = domains[domain_choice]

# Action choices
options = ["📄 View Records", "➕ Add New Record", "✏ Update / Delete", "📊 Charts / Insights"]
actions = st.sidebar.multiselect("Select Actions", options, default=["📄 View Records"])

# Load data for selected domain
if "df" not in st.session_state or st.session_state.get("domain") != domain_choice:
    df = domain_data["get_df"]()
    st.session_state.df = df
    st.session_state.domain = domain_choice
else:
    df = st.session_state.df

# Helper function to refresh dataframe
def refresh_data():
    st.session_state.df = domain_data["get_df"]()

# ============================= VIEW RECORDS =============================
if "📄 View Records" in actions:
    filters = {}
    if domain_choice == "Cybersecurity":
        filters = {"severity": df["severity"].unique(), "status": df["status"].unique()} if not df.empty else {}
    elif domain_choice == "IT Operations":
        filters = {"priority": df["priority"].unique(), "status": df["status"].unique()} if not df.empty else {}
    view_records(domain_choice, df, filters)

# ============================= ADD NEW RECORD =============================
if "➕ Add New Record" in actions:
    add_new_record(
        domain_choice,
        insert_func=lambda **kwargs: domain_data["insert_func"](conn, **kwargs),
        form_fields=domain_data["fields"]
    )
    refresh_data()

# ============================= UPDATE / DELETE =============================
if "✏ Update / Delete" in actions:
    update_delete_record(
        domain_choice,
        df,
        update_func=lambda id, **kwargs: domain_data["update_func"](conn, id, **kwargs),
        delete_func=lambda id: domain_data["delete_func"](conn, id),
        update_fields=domain_data["fields"]
    )
    refresh_data()

# ============================= CHARTS / INSIGHTS =============================
if "📊 Charts / Insights" in actions:
    st.subheader(f"📊 {domain_choice} Analytics")
    if df.empty:
        st.info("No data available for charts.")
    else:
        for chart_func in domain_data["charts"]:
            result = chart_func(conn)
            st.write(f"📌 {chart_func.__name__}")
            st.dataframe(result, use_container_width=True)
