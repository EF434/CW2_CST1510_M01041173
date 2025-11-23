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
# ---- DATABASE CONNECTION (Only once here) ----
conn = connect_database("DATA/intelligence_platform.db")


# ---------- DOMAIN WRAPPER FUNCTIONS ----------
def load_data(domain):
    """Return dataframe, fields and CRUD functions based on the domain."""
    
    if domain == "Cybersecurity":
        

    elif domain == "IT Operations":
        

    elif domain == "Data Science":
        \\