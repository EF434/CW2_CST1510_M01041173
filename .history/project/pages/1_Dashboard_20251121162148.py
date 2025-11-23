import sys, os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np

from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident

# ----------------------------
# Database connection
# ----------------------------
from app.data.db import connect_database
conn = connect_database('DATA/intelligence_platform.db')

# ----------------------------
# Dark theme & orange styling
# ----------------------------
st.markdown(
    """
    <style>
    .main { background-color: #0D0D0D; color: white; }
    .stButton>button { background-color: orange; color: black; font-weight: bold; }
    .stSelectbox>div>div>div>select { background-color: #333333; color: white; }
    .stTextInput>div>input { background-color: #222222; color: white; }
    .stDataFrame { background-color: #0D0D0D; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Page title
# ----------------------------
st.title("🌐 Multi-Domain Dashboard")

# ----------------------------
# Domain selection
# ----------------------------
domains = ["Cybersecurity", "Data Science", "IT Operations"]
selected_domain = st.sidebar.selectbox("Select Domain", domains)

st.markdown(f"<h3 style='color: orange;'>Selected Domain: {selected_domain}</h3>", unsafe_allow_html=True)

# ----------------------------
# Domain-specific dashboards
# ----------------------------
if selected_domain == "Cybersecurity":
    st.subheader("📋 Cybersecurity Incidents")
    
    # -------------------- Load Incidents --------------------
df = get_all_incidents(conn)

st.title("🛡 Cybersecurity Incident Dashboard")

if df.empty:
    st.warning("⚠ No incidents found. Add one below.")
else:

    # Ensure proper date formatting
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date

    # -------------------- Sidebar Filters --------------------
    with st.sidebar:
        st.header("Filters")

        # Filter by severity
        severity_filter = st.multiselect(
            "Severity Level",
            options=df["severity"].unique(),
            default=df["severity"].unique()
        )

        # Filter by status
        status_filter = st.multiselect(
            "Incident Status",
            options=df["status"].unique(),
            default=df["status"].unique()
        )

    # Apply filters
    filtered = df[
        (df["severity"].isin(severity_filter)) &
        (df["status"].isin(status_filter))
    ]

    st.caption(f"Showing {len(filtered)} filtered cybersecurity incidents")

    # -------------------- Layout w/ Charts --------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Incidents by Severity")
        sev_data = filtered.groupby("severity").size()
        st.bar_chart(sev_data)

    with col2:
        st.subheader("Incidents Over Time")
        if "date" in filtered.columns:
            date_data = filtered.groupby("date").size()
            st.area_chart(date_data)
        else:
            st.info("No date field found to generate time chart.")

    # -------------------- Show Table --------------------
    with st.expander("View Filtered Incident Data"):
        st.dataframe(filtered, use_container_width=True)


# -------------------- Add New Incident --------------------
st.subheader("➕ Add New Incident")

with st.form("add_form"):
    title = st.text_input("Incident Title")
    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
    submitted = st.form_submit_button("Add Incident")

    if submitted:
        if title.strip():
            insert_incident(conn, title.strip(), severity, status)
            st.success("Incident successfully added!")
            st.experimental_rerun()
        else:
            st.error("⚠ Title cannot be empty.")