import streamlit as st
import pandas as pd
import numpy as np

from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident

st.set_page_config(page_title="Cybersecurity Dashboard", layout="wide")

# -------------------- DB Connection --------------------
conn = connect_database("DATA/intelligence_platform.db")

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
