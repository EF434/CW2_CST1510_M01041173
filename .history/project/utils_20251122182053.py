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
    insert_ticket, update_ticket, 
    delete_ticket, get_unresolved_tickets, 
    get_ticket_delays)
)

# Data Science
from app.data.datasets import (
     insert_dataset, update_dataset, 
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

def view_records():
    incidents = get_all_incidents(conn) # Your Week 8 function!
    st.dataframe(incidents, use_container_width=True)
    
def add_new_record():
   if"records"not inst.session_state:
st.session_state.records = []

# Create form
withst.form("add_record"):
 name = st.text_input("Name")
 email = st.text_input("Email")
 role = st.selectbox("Role", ["User", "Admin"])

ifst.form_submit_button("Add Record"):
 record = {"name": name, "email": email,
 &: role}
st.session_state.records.append(record)
st.success("Record added!")
    
def update_delete_record():
    pass
def data_visualization():
    pass