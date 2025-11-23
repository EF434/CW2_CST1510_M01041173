# ------------------- IMPORTS -------------------
import streamlit as st
import os
import sys

# Path setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

# ------------ DB + Modules ------------
from app.data.db import connect_database, load_all_csv_data
from app.data.schema import create_all_tables

# Utility functions
from utils import view_records, add_new_record, update_delete_record, data_visualization

# ------------------- DATABASE -------------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DB_FILE = os.path.join(DATA_DIR, "intelligence_platform.db")

conn = connect_database(DB_FILE)
create_all_tables(conn)

load_all_csv_data(conn, os.path.join(DATA_DIR, "cyber_incidents.csv"), "cyber_incidents")
load_all_csv_data(conn, os.path.join(DATA_DIR, "it_tickets.csv"), "it_tickets")
load_all_csv_data(conn, os.path.join(DATA_DIR, "datasets_metadata.csv"), "datasets_metadata")
"""
# ------------------- LOGIN CHECK -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("You must be logged in.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()
"""
# ------------------- UI HEADER -------------------
st.set_page_config(page_title="Dashboard", layout="wide", page_icon="logo.png")
st.markdown(
    """<h1 style='text-align: center; color: #1f77b4; font-family: "Segoe UI", sans-serif;'>
    Multi-Domain Intelligence Platform
    </h1>""",
    unsafe_allow_html=True
)

# ------------------- SIDEBAR -------------------
domain = st.sidebar.selectbox("Select Domain", ["Cybersecurity", "IT Operations", "Data Science"])
options = ["📄 View Records", "➕ Add New Record", "✏ Update / Delete", "📊 Charts / Insights"]
actions = st.sidebar.multiselect("Select Actions", options, default=["📄 View Records"])

# ------------------- ACTIONS -------------------
table_map = {
    "Cybersecurity": "cyber_incidents",
    "IT Operations": "it_tickets",
    "Data Science": "datasets_metadata"
}

table_name = table_map[domain]

if "📄 View Records" in actions:
    view_records(conn, table_name)
if "➕ Add New Record" in actions:
    add_new_record(conn, table_name)
if "✏ Update / Delete" in actions:
    update_delete_record(conn, table_name)
if "📊 Charts / Insights" in actions:
    data_visualization(conn, table_name)
    if st.button("Data"):
        st.switch_page("Analytics.py")
    st.stop()

# ------------------- LOGOUT -------------------
st.divider()
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.success("Logged out!")
    st.switch_page("Home.py")

