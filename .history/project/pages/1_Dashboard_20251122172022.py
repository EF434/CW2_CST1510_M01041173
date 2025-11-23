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
st.title("🧠 Multi-Domain Intelligence Platform")


# ------------------- SIDEBAR -------------------
domain = st.sidebar.selectbox("Select Domain", ["Cybersecurity", "IT Operations", "Data Science"])
actions = st.sidebar.selectbox("Choose Action", ["● View Records", "● Add New Recor", "Data Science"])
actions = st.sidebar.radio("Choose Action", ["View", "Add", "Update", "Delete"])


# ------------------- LOAD DATA FUNCTION -------------------
def load_data():
    if domain == "Cybersecurity":
        return pd.DataFrame(get_all_incidents(conn))
    elif domain == "IT Operations":
        return pd.DataFrame(get_unresolved_tickets(conn))
    else:
        return pd.DataFrame(list_datasets_by_source(conn))


df = load_data()


# ------------------- DOMAIN MAPPING -------------------
if domain == "Cybersecurity":
    insert_func = insert_incident
    update_func = update_incident_status
    delete_func = delete_incident
    fields = ["title", "severity", "status", "description", "reported_by"]

elif domain == "IT Operations":
    insert_func = insert_ticket
    update_func = update_ticket
    delete_func = delete_ticket
    fields = ["title", "priority", "status", "assigned_to"]

else:  # Data Science
    insert_func = insert_dataset
    update_func = update_dataset
    delete_func = delete_dataset
    fields = ["dataset_name", "source", "last_updated", "size"]


# ------------------- ACTION ROUTING -------------------
if actions == "View":
    st.subheader(f"📄 {domain} Records")
    st.dataframe(df, use_container_width=True)

elif actions == "Add":
    add_record_form(fields, insert_func, conn)

elif actions == "Update":
    update_record_form(df, update_func, fields, conn)

elif actions == "Delete":
    delete_record_form(df, delete_func, conn)


# ------------------- LOGOUT -------------------
st.divider()
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.success("Logged out!")
    st.switch_page("Home.py")
