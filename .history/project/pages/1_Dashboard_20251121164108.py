import sys, os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

import streamlit as st
import pandas as pd
from datetime import datetime

from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident

# ---------------------------- CONFIG & STYLE ----------------------------
st.set_page_config(page_title="Cyber Intelligence Platform", layout="wide")

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

# ---------------------------- DATABASE ----------------------------
conn = connect_database("DATA/intelligence_platform.db")

# ---------------------------- PAGE TITLE ----------------------------
st.title("🌐 Unified Intelligence Platform")


# ---------------------------- SIDEBAR NAVIGATION ----------------------------
st.sidebar.header("🔍 Navigation")

domains = {
    "Cybersecurity": "Manage incidents",
    "Data Science": "Datasets metadata",
    "IT Operations": "IT ticket system"
}

domain_choice = st.sidebar.selectbox("Select Domain", list(domains.keys()))

# Action choices based on the selected domain
actions = ["📄 View Records", "➕ Add New Record", "📊 View Insights / Charts"]
selected_action = st.sidebar.radio("Select Action", actions)

st.markdown(f"<h3 style='color: orange;'>{domain_choice} — {selected_action}</h3>", unsafe_allow_html=True)


# ============================= CYBERSECURITY SECTION =============================
if domain_choice == "Cybersecurity":

    df = get_all_incidents(conn)

    if selected_action == "📄 View Records":
        st.subheader("📄 Cybersecurity Incidents Table")

        if not df.empty:
            # Filters
            with st.expander("🔍 Apply Filters"):
                severity_filter = st.multiselect(
                    "Filter by Severity", df["severity"].unique(), default=df["severity"].unique()
                )
                status_filter = st.multiselect(
                    "Filter by Status", df["status"].unique(), default=df["status"].unique()
                )

            filtered_df = df[df["severity"].isin(severity_filter) & df["status"].isin(status_filter)]

            st.write(f"Showing {len(filtered_df)} filtered records")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No incident records found.")

    # ---------- ADD RECORD ----------
    elif selected_action == "➕ Add New Record":
        st.subheader("➕ Add Cybersecurity Incident")

        with st.form("incident_form"):
            incident_title = st.text_input("Incident Title")
            incident_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            incident_status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            description = st.text_area("Description (optional)")

            submitted = st.form_submit_button("Save Incident")

            if submitted:
                if incident_title.strip():
                    insert_incident(conn, incident_title.strip(), incident_severity, incident_status)
                    st.success("✔ Incident successfully added!")
                    st.experimental_rerun()
                else:
                    st.error("⚠ Title is required.")

    # ---------- CHARTS ----------
    elif selected_action == "📊 View Insights / Charts":
        st.subheader("📊 Incident Analytics")

        if df.empty:
            st.info("No data available to display analytics.")
        else:
            col1, col2 = st.columns(2)

            # INCIDENT SEVERITY CHART
            with col1:
                st.write("Severity Distribution")
                st.bar_chart(df["severity"].value_counts())

            # INCIDENT STATUS CHART
            with col2:
                st.write("Status Over Time")
                if "date" in df.columns:
                    chart_df = df.groupby("date").size()
                    st.area_chart(chart_df)
                else:
                    st.warning("No date field detected.")

# ================================== OTHER DOMAINS PLACEHOLDERS ================================

elif domain_choice == "Data Science":
    st.info("📦 Data Science module will use datasets_metadata table functions.")

elif domain_choice == "IT Operations":
    st.info("⚙️ IT Operations module will use it_tickets table functions.")

