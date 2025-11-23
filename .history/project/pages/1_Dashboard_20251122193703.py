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



# Utility functions
from utils import cyber_incidents_func, it_tickets_func, datasets_metadata_func



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



def cyber_incidents_func():
    if "📄 View Records" in actions:
        view_records(conn, "cyber_incidents")
    if "➕ Add New Record" in actions:
        add_new_record(conn, "cyber_incidents")
    if "✏ Update / Delete" in actions:
        update_delete_record(conn, "cyber_incidents")
    if "📊 Charts / Insights" in actions:
        data_visualization(conn, "cyber_incidents")


def it_tickets_func():
    if "📄 View Records" in actions:
        view_records(conn, "it_tickets")
    if "➕ Add New Record" in actions:
        add_new_record(conn, "it_tickets")
    if "✏ Update / Delete" in actions:
        update_delete_record(conn, "it_tickets")
    if "📊 Charts / Insights" in actions:
        data_visualization(conn, "it_tickets")


def datasets_metadata_func():
    if "📄 View Records" in actions:
        view_records(conn, "datasets_metadata")
    if "➕ Add New Record" in actions:
        add_new_record(conn, "datasets_metadata")
    if "✏ Update / Delete" in actions:
        update_delete_record(conn, "datasets_metadata")
    if "📊 Charts / Insights" in actions:
        data_visualization(conn, "datasets_metadata")

if domain == "Cybersecurity":
    cyber_incidents_func()
elif domain == "IT Operations":
    it_tickets_func()
else:
    datasets_metadata_func()

# ------------------- LOGOUT -------------------
st.divider()
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.success("Logged out!")
    st.switch_page("Home.py")
