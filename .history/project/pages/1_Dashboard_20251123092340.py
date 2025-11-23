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

# ------------------- LOGIN CHECK -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("You must be logged in.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# ------------------- UI HEADER -------------------
st.set_page_config(page_title="Dashboard", layout="centered", page_icon="logo.png")
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

# ------------------- LOGOUT -------------------
st.divider()
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.success("Logged out!")
    st.switch_page("Home.py")
# Import Streamlit and Week 8 functions
import streamlit as st
from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident

# Connect to database (Week 8 function)
conn = connect_database('DATA/intelligence_platform.db')

# Page title
st.title("Cyber Incidents Dashboard")

# READ: Display incidents in a beautiful table (Week 8 function + Streamlit UI)
incidents = get_all_incidents(conn)  # ← Week 8 function handles SQL
st.dataframe(incidents, use_container_width=True)  # ← Streamlit creates UI

# CREATE: Add new incident with a form
with st.form("new_incident"):
    # Form inputs (Streamlit widgets)
    title = st.text_input("Incident Title")
    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])

    # Form submit button
    submitted = st.form_submit_button("Add Incident")

    # When form is submitted
    if submitted and title:
        # Call Week 8 function to insert into database
        insert_incident(conn, title, severity, status)  # ← Week 8 function!
        st.success("✓ Incident added successfully!")
        st.rerun()  # Refresh the page to show new incident