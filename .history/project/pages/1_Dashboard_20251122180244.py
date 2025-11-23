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
    get_all_incidents, insert_incident,
    update_incident_status, delete_incident
)

# IT Ops
from app.data.tickets import (
    get_unresolved_tickets, insert_ticket,
    update_ticket, delete_ticket
)

# Data Science
from app.data.datasets import (
    list_datasets_by_source, insert_dataset,
    update_dataset, delete_dataset
)



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
st.set_page_config(page_title="Dashboard", layout="wide")
st.markdown(""" <h1 style='text-align: center; color: #1f77b4; font-family: "Segoe UI", sans-serif;'>
             Multi-Domain Intelligence Platform </h1> """,unsafe_allow_html=True )


# ------------------- SIDEBAR -------------------
domain = st.sidebar.selectbox("Select Domain", ["Cybersecurity", "IT Operations", "Data Science"])
options = ["📄 View Records", "➕ Add New Record", "✏ Update / Delete", "📊 Charts / Insights"]
actions = st.sidebar.multiselect("Select Actions", options, default=["📄 View Records"])

# ------------------- LOGOUT -------------------
st.divider()
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.success("Logged out!")
    st.switch_page("Home.py")

if domain == "Cybersecurity":
    view_records()
    
elif domain == "IT Operations":
    pass
if domain == "Cybersecurity":
    pass