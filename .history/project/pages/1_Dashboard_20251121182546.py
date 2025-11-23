import sys, os
from pathlib import Path
import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------- BASE DIR -----------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from app.data.db import connect_database, load_all_csv_data
from app.data.incidents import get_all_incidents, insert_incident
from app.data.tickets import get_unresolved_tickets, insert_ticket
from app.data.datasets import get_top_recent_updates, insert_dataset, display_resource_usage

# ----------------- CONFIG -----------------
st.set_page_config(page_title="Unified Intelligence Platform", layout="wide")
st.markdown("""
<style>
.main { background-color: #0D0D0D; color: white; }
.stButton>button { background-color: orange; color: black; font-weight: bold; }
.stSelectbox>div>div>div>select { background-color: #333333; color: white; }
.stTextInput>div>input { background-color: #222222; color: white; }
.stDataFrame { background-color: #0D0D0D; color: white; }
</style>
""", unsafe_allow_html=True)

# ----------------- DATABASE -----------------
DATA_DIR = BASE_DIR / "DATA"
DB_PATH = DATA_DIR / "intelligence_platform.db"
conn = connect_database(DB_PATH)

# ----------------- DOMAIN SELECTION -----------------
st.sidebar.header("🔍 Navigation")
domains = ["Cybersecurity", "IT Operations", "Data Science"]
domain_choice = st.sidebar.selectbox("Select Domain", domains)

actions = ["📄 View Records", "➕ Add New Record", "📊 View Insights / Charts"]
selected_action = st.sidebar.radio("Select Action", actions)

st.markdown(f"<h3 style='color: orange;'>{domain_choice} — {selected_action}</h3>", unsafe_allow_html=True)

# ----------------- CYBERSECURITY -----------------
if domain_choice == "Cybersecurity":
    csv_path = DATA_DIR / "cyber_incidents.csv"
    df = get_all_incidents(conn)
    if df.empty:
        load_all_csv_data(conn, csv_path, "cyber_incidents")
        df = get_all_incidents(conn)

    if selected_action == "📄 View Records":
        st.subheader("📄 Cybersecurity Incidents Table")
        if not df.empty:
            with st.expander("🔍 Apply Filters"):
                severity_filter = st.multiselect("Filter by Severity", df["severity"].unique(), default=df["severity"].unique())
                status_filter = st.multiselect("Filter by Status", df["status"].unique(), default=df["status"].unique())
            filtered_df = df[df["severity"].isin(severity_filter) & df["status"].isin(status_filter)]
            st.write(f"Showing {len(filtered_df)} filtered records")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No incident records found.")

    elif selected_action == "➕ Add New Record":
        st.subheader("➕ Add Cybersecurity Incident")
        with st.form("incident_form"):
            date = st.date_input("Incident Date", datetime.today())
            incident_type = st.text_input("Incident Type (e.g., Phishing, Malware)")
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            description = st.text_area("Description")
            submitted = st.form_submit_button("Save Incident")
            if submitted:
                if incident_type.strip():
                    insert_incident(conn, date.strftime("%Y-%m-%d"), incident_type.strip(), severity, status, description)
                    st.success("✔ Incident successfully added!")
                    st.experimental_rerun()
                else:
                    st.error("⚠ Incident type is required.")

    elif selected_action == "📊 View Insights / Charts":
        st.subheader("📊 Cybersecurity Analytics")
        if not df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.write("Severity Distribution")
                st.bar_chart(df["severity"].value_counts())
            with col2:
                st.write("Status Over Time")
                if "date" in df.columns:
                    chart_df = df.groupby("date").size()
                    st.area_chart(chart_df)
                else:
                    st.warning("No 'date' column available for chart.")
        else:
            st.info("No data to display analytics.")

# ----------------- IT OPERATIONS -----------------
elif domain_choice == "IT Operations":
    csv_path = DATA_DIR / "it_tickets.csv"
    df = get_unresolved_tickets(conn)
    if df.empty:
        load_all_csv_data(conn, csv_path, "it_tickets")
        df = get_unresolved_tickets(conn)

    if selected_action == "📄 View Records":
        st.subheader("📄 IT Tickets Table")
        st.dataframe(df, use_container_width=True)

    elif selected_action == "➕ Add New Record":
        st.subheader("➕ Add IT Ticket")
        with st.form("ticket_form"):
            ticket_id = st.text_input("Ticket ID")
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            category = st.text_input("Category")
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            submitted = st.form_submit_button("Save Ticket")
            if submitted:
                if ticket_id.strip() and subject.strip():
                    insert_ticket(conn, ticket_id.strip(), priority, status, category, subject, description)
                    st.success("✔ Ticket successfully added!")
                    st.experimental_rerun()
                else:
                    st.error("⚠ Ticket ID and Subject are required.")

    elif selected_action == "📊 View Insights / Charts":
        st.subheader("📊 IT Tickets Analytics")
        if not df.empty:
            unresolved_by_staff, unresolved_by_status = df.groupby("assigned_to").size(), df.groupby("status").size()
            col1, col2 = st.columns(2)
            with col1:
                st.write("Unresolved Tickets by Staff")
                st.bar_chart(unresolved_by_staff)
            with col2:
                st.write("Unresolved Tickets by Status")
                st.bar_chart(unresolved_by_status)
        else:
            st.info("No unresolved tickets to display.")

# ----------------- DATA SCIENCE -----------------
elif domain_choice == "Data Science":
    csv_path = DATA_DIR / "datasets_metadata.csv"
    df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
    if df.empty:
        load_all_csv_data(conn, csv_path, "datasets_metadata")
        df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)

    if selected_action == "📄 View Records":
        st.subheader("📄 Datasets Metadata Table")
        st.dataframe(df, use_container_width=True)

    elif selected_action == "➕ Add New Record":
        st.subheader("➕ Add Dataset")
        with st.form("dataset_form"):
            dataset_name = st.text_input("Dataset Name")
            category = st.text_input("Category")
            source = st.text_input("Source")
            last_updated = st.date_input("Last Updated")
            record_count = st.number_input("Record Count", min_value=0)
            file_size_mb = st.number_input("File Size (MB)", min_value=0.0)
            submitted = st.form_submit_button("Save Dataset")
            if submitted:
                if dataset_name.strip():
                    insert_dataset(conn, dataset_name.strip(), source, category, last_updated.strftime("%Y-%m-%d"),
                                   record_count, file_size_mb)
                    st.success("✔ Dataset successfully added!")
                    st.experimental_rerun()
                else:
                    st.error("⚠ Dataset Name is required.")

    elif selected_action == "📊 View Insights / Charts":
        st.subheader("📊 Dataset Analytics")
        if not df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.write("Top 3 Recent Updates")
                st.dataframe(get_top_recent_updates(conn))
            with col2:
                st.write("Resource Usage by Dataset")
                st.bar_chart(display_resource_usage(conn).set_index("dataset_name")["file_size_mb"])
        else:
            st.info("No datasets to analyze.")
