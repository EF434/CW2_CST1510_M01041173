# ------------ Import Modules ------------
import sys
import os
import streamlit as st
import pandas as pd
from pathlib import Path

# ------------ BASE SETUP ------------
DATA_DIR = Path(__file__).parents[1]  # Two levels up
sys.path.append(str(DATA_DIR))

DATA_DIR = DATA_DIR / "DATA"
DATA_DIR.mkdir(exist_ok=True) 

DB_FILE = DATA_DIR / "intelligence_platform.db"

# ------------ DATABASE SETUP ------------
conn = connect_database(DB_FILE)
create_all_tables(conn)

# ------------ LOAD CSV DATA ------------
csv_files = {
    "cyber_incidents": "cyber_incidents.csv",
    "it_tickets": "it_tickets.csv",
    "datasets_metadata": "datasets_metadata.csv"
}

for table, filename in csv_files.items():
    load_all_csv_data(conn, os.path.join(DATA_DIR, filename), table)
    
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


                      
# ---------- Session state ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Login"

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()


# ------------ STREAMLIT CONFIG ------------
st.set_page_config(page_title="Unified Intelligence Platform", layout="wide")
st.markdown(
    """
    <h1 style='text-align: center; color: #1f77b4; font-family: "Segoe UI", sans-serif;'>
         Multi-Domain Intelligence Platform
    </h1>
    """,
    unsafe_allow_html=True
)

# ------------ DATABASE SETUP ------------
DB_FILE = os.path.join(DATA_DIR, "DATA", "intelligence_platform.db")
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
