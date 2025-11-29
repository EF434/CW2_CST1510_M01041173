# ------------------- IMPORTS -------------------
import streamlit as st
import pandas as pd
import numpy as np
import time
import sys
import os
from openai import OpenAI
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt

# ------------------- PATH SETUP -------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

# ------------------- MODULES -------------------
from app.data.db import connect_database, load_all_csv_data
from app.data.schema import create_all_tables

# Cybersecurity
from app.data.incidents import (
    get_all_incidents, get_incidents_by_type_count, 
    get_high_severity_by_status, get_incident_types_with_many_cases, 
    get_incident_trend, unresolved_incidents_by_type,
    get_threat_spike, get_resolution_bottleneck
)

# IT Ops
from app.data.tickets import (
    get_ticket_trend, get_all_tickets,
    update_ticket, delete_ticket,
    get_unresolved_tickets, get_ticket_delays
)

# Data Science
from app.data.datasets import (
    insert_dataset, update_dataset, get_all_datasets,
    list_datasets_by_source, delete_dataset,
    get_top_recent_updates, display_resource_usage
)


# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Wave - AI Incident Analyzer", layout="wide", page_icon="logo.png")

# ------------------- DATABASE -------------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DB_FILE = os.path.join(DATA_DIR, "intelligence_platform.db")

conn = connect_database(DB_FILE)
create_all_tables(conn)

# ------------------- INITIALIZE DATA -------------------
df_incidents = get_all_incidents(conn)
df_tickets = get_all_tickets(conn)
df_datasets = get_all_datasets(conn)

# ------------------- OPENAI CLIENT -------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------- PAGE CONTENT -------------------
st.title("🔍 AI Incident Analyzer")

if not df_incidents.empty:
    # Convert to list of dicts
    incidents_list = df_incidents.to_dict(orient="records")
    
    # Select incident
    incident_options = [
        f"{inc['id']}: {inc['incident_type']} - {inc['severity']}" for inc in incidents_list
    ]
    
    selected_idx = st.selectbox(
        "Select incident to analyze:",
        range(len(incidents_list)),
        format_func=lambda i: incident_options[i]
    )
    
    incident = incidents_list[selected_idx]
    
    # Show details
    st.subheader("📋 Incident Details")
    st.write(f"**Type:** {incident['incident_type']}")
    st.write(f"**Severity:** {incident['severity']}")
    st.write(f"**Description:** {incident['description']}")
    st.write(f"**Status:** {incident['status']}")
    
    # Analyze with AI
    if st.button("🤖 Analyze with AI"):
        with st.spinner("AI analyzing incident..."):
            analysis_prompt = f"""Analyze this cybersecurity incident:

Type: {incident['incident_type']}
Severity: {incident['severity']}
Description: {incident['description']}
Status: {incident['status']}

Provide:
1. Root cause analysis
2. Immediate actions needed
3. Long-term prevention measures
4. Risk assessment"""
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a cybersecurity expert."},
                        {"role": "user", "content": analysis_prompt}
                    ]
                )
                analysis = response.choices[0].message.content
                st.subheader("🧠 AI Analysis")
                st.write(analysis)
            except Exception as e:
                st.error(f"AI analysis failed: {e}")
else:
    st.info("No incidents found in the database.")
