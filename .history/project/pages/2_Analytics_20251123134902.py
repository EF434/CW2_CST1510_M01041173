# ------------------- IMPORTS -------------------
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

# Path setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

# ------------  Modules ------------
from app.data.db import connect_database, load_all_csv_data
from app.data.schema import create_all_tables

# Cybersecurity
from app.data.incidents import (
     insert_incident, get_all_incidents,
    update_incident_status, delete_incident,
    get_incidents_by_type_count, get_high_severity_by_status,
    get_incident_types_with_many_cases, get_incident_trend, unresolved_incidents_by_type
)

# IT Ops
from app.data.tickets import (
    insert_ticket, get_all_tickets,
    update_ticket, delete_ticket,
    get_unresolved_tickets, get_ticket_delays
)

# Data Science
from app.data.datasets import (
     insert_dataset, update_dataset, get_all_datasets,
     list_datasets_by_source, delete_dataset,
     get_top_recent_updates, display_resource_usage
)

# ------------------- DATABASE -------------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DB_FILE = os.path.join(DATA_DIR, "intelligence_platform.db")

conn = connect_database(DB_FILE)
create_all_tables(conn)

domain = st.sidebar.selectbox("Select Domain", ["Cybersecurity", "IT Operations", "Data Science"])
# ------------------- DATA VISUALIZATION -------------------

def data_visualization(conn, table_name):
    if domain == "Cybersecurity":


data_visualization(domain)

# ------------------- IMPORTS -------------------
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys

# Path setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

# ------------ DB + Modules ------------
from app.data.db import connect_database
from app.data.incidents import (
    get_all_incidents, get_incidents_by_type_count, get_high_severity_by_status,
    get_incident_types_with_many_cases, get_incident_trend, unresolved_incidents_by_type
)
from app.data.tickets import get_all_tickets
from app.data.datasets import get_all_datasets

# ------------------- DATABASE -------------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DB_FILE = os.path.join(DATA_DIR, "intelligence_platform.db")

conn = connect_database(DB_FILE)

# ------------------- UI HEADER -------------------
st.set_page_config(page_title="Analytics", layout="wide", page_icon="📊")
st.title("📊 Analytics & Visualizations")

# ------------------- DOMAIN SELECTION -------------------
domain = st.selectbox("Select Domain to Visualize", ["Cybersecurity", "IT Operations", "Data Science"])


