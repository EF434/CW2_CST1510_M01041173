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

# ------------------- SESSION STATE -------------------
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False 
if "username" not in st.session_state: 
    st.session_state.username = ""
if "df" not in st.session_state: 
    st.session_state.df = pd.DataFrame() # empty placeholder 
if "domain" not in st.session_state: 
    st.session_state.domain = ""


# ------------------- ACCESS CONTROL -------------------
# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# ------------------- UI CONFIG -------------------
st.set_page_config(page_title="Dashboard", layout="wide")
st.markdown(
    "<h1 style='text-align:center;color:#1f77b4;font-family:Segoe UI;'>"
    "Multi-Domain Intelligence Platform</h1>",
    unsafe_allow_html=True
)

# ------------------- SIDEBAR CONTROLS -------------------
domain_choice = st.sidebar.selectbox(
    "Select Domain",
    ADD_CONFIG.keys()
)

actions = st.sidebar.multiselect(
    "Select Actions",
    ["● View Records", "● Add New Record", "● Update / Delete", "📊 Charts / Insights"],
    default=["● View Records"]
)

# ------------------- DATA LOADING -------------------
def refresh_data():
    """Reload domain data into session state."""
    if domain_choice == "Cybersecurity":
        st.session_state.df = get_all_incidents(conn)
    elif domain_choice == "IT Operations":
        st.session_state.df = get_unresolved_tickets(conn)
    elif domain_choice == "Data Science":
        st.session_state.df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)

refresh_data()
df = st.session_state.df
st.session_state.domain = domain_choice

# ------------------- FILTER SETTINGS -------------------
filter_columns = {
    "Cybersecurity": {"severity": ["Low", "Medium", "High", "Critical"],
                      "status": ["Open", "Investigating", "Resolved", "Closed"],
                      "incident_type": ["Phishing", "Malware", "DDoS", "Ransomware"]},
    "IT Operations": {"priority": ["Low", "Medium", "High", "Critical"],
                      "status": ["Open", "In Progress", "Resolved", "Closed"],
                      "category": ["Biology", "In Progress", "Resolved", "Closed"]},
    "Data Science": {}
}

# ------------------- DYNAMIC FUNCTION MAPPING -------------------
UPDATE_DELETE_MAP = {
    "Cybersecurity": (update_incident_status, delete_incident),
    "IT Operations": (update_ticket, delete_ticket),
    "Data Science": (update_dataset, delete_dataset)
}

CHARTS_MAP = {
    "Cybersecurity": [get_incidents_by_type_count, get_high_severity_by_status],
    "IT Operations": [get_ticket_delays],
    "Data Science": [get_top_recent_updates, display_resource_usage, list_datasets_by_source]
}

# ------------------- ACTION HANDLING -------------------
for action in actions:
    if action == "● View Records":
        view_records(domain_choice, df, filter_columns.get(domain_choice))
    
    elif action == "● Add New Record":
        config = ADD_CONFIG.get(domain_choice)
        if config:
            add_new_record(domain_choice, config["insert_func"], config["form_fields"])
            refresh_data()

    elif action == "● Update / Delete":
        update_func, delete_func = UPDATE_DELETE_MAP[domain_choice]
        form_fields = ADD_CONFIG[domain_choice]["form_fields"]
        update_delete_record(domain_choice, df, update_func, delete_func, form_fields)
        refresh_data()

    elif action == "📊 Charts / Insights":
        st.subheader(f"📊 {domain_choice} Analytics")
        if df.empty:
            st.info("No data available for analytics.")
        else:
            for chart in CHARTS_MAP.get(domain_choice, []):
                st.write(f"📌 {chart.__name__}")
                st.dataframe(chart(conn), use_container_width=True)

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")