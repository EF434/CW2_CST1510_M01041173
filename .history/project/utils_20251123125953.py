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


# ------------------- VIEW RECORDS -------------------
def view_records(conn, table_name):
    st.markdown(
            """
            <style>
            .cyber-sub {
                font-family: "Segoe UI", Roboto, sans-serif;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 0.6px;
                color: #0b3d91;
                margin: 0;
                padding-bottom: 6px;
                display: inline-block;
                border-bottom: 4px solid #ff4b4b;
            }
            </style>
            <div class="cyber-sub">🔒 {table}</div>
            """,
            unsafe_allow_html=True
        )
    if table_name == "cyber_incidents":
        df = get_all_incidents(conn)

        # Sidebar filters
        severity_filter = st.multiselect(
            "Select Severity",
            ["Low", "Medium", "High", "Critical"]
        )

        status_filter = st.multiselect(
            "Select Status",
            ["Open", "Investigating", "Resolved", "Closed"]
        )

        # Apply filters only if something is selected
        filtered_df = df[
            (df["severity"].isin(severity_filter) ) &
            (df["status"].isin(status_filter))
        ]
    elif table_name == "it_tickets":
        df = get_all_tickets(conn)
        st.subheader("IT Tickets")
    elif table_name == "datasets_metadata":
        df = get_all_datasets(conn)
        st.subheader("Data Science")

            # Filters
        category = st.sidebar.multiselect(
            "Dataset Category",
            options=df["category"].unique(),
            default=df["category"].unique()
        )

        last_updated = st.sidebar.date_input(
            "Last Updated Range",
            value=(df["last_updated"].min(), df["last_updated"].max())
        )

    else:
        st.error("Unknown table")
        return

    st.caption(f"Showing {len(filtered_df)} incidents after filtering.")
    with st.expander("See Filtered Incident Data"):
            st.dataframe(filtered_df, use_container_width=True)


# ------------------- ADD NEW RECORD -------------------
def add_new_record(conn, table_name):
    if table_name == "cyber_incidents":
        st.subheader("Add New Cybersecurity Incident")
        with st.form("add_incident"):
            date = st.date_input("Date")
            incident_type = st.selectbox("Incident Type", ["Phishing", "Malware", "DDoS", "Ransomware"])
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            description = st.text_area("Description")
            reported_by = st.text_input("Reported by")
            submitted = st.form_submit_button("Add Incident")
            if submitted:
                insert_incident(conn, str(date), incident_type, severity, status, description, reported_by)
                st.success("✓ Incident added successfully!")
                st.rerun()

    elif table_name == "it_tickets":
        st.subheader("Add New IT Ticket")
        with st.form("add_ticket"):
            ticket_id = st.text_input("Ticket ID")
            priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            category = st.text_input("Category")
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            created_date = st.date_input("Created Date")
            resolved_date = st.date_input("Resolved Date", value=None)
            assigned_to = st.text_input("Assigned To")
            submitted = st.form_submit_button("Add Ticket")
            if submitted:
                insert_ticket(conn, ticket_id, priority, status, category, subject, description,
                              str(created_date), str(resolved_date), assigned_to)
                st.success("✓ Ticket added successfully!")
                st.rerun()

    elif table_name == "datasets_metadata":
        st.subheader("Add New Dataset Metadata")
        with st.form("add_dataset_form"):
            dataset_name = st.text_input("Dataset Name")
            category = st.selectbox("Category", ["Threat Intelligence", "Network Logs", "User Data", "Other"])
            source = st.text_input("Source / Origin")
            last_updated = st.date_input("Last Updated")
            record_count = st.number_input("Record Count", min_value=0, step=1)
            file_size_mb = st.number_input("File Size (MB)", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Add Dataset")
            if submitted:
                try:
                    insert_dataset(conn, dataset_name, category, source, str(last_updated), record_count, file_size_mb)
                    st.success(f"✓ Dataset '{dataset_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add dataset: {e}")


def update_delete_record(conn, table_name):

    # ------------------- Get Records -------------------
    if table_name == "cyber_incidents":
        records = get_all_incidents(conn)
        key = "id"
    elif table_name == "it_tickets":
        records = get_all_tickets(conn)
        key = "ticket_id"
    elif table_name == "datasets_metadata":
        records = get_all_datasets(conn)
        key = "dataset_name"
    else:
        st.error("Unknown table name")
        return

    if records.empty:
        st.info("No records available to update or delete.")
        return

    record_list = records.to_dict("records")
    ids = [r[key] for r in record_list]
    selected = st.selectbox(f"Select record ({key})", ids)
    idx = ids.index(selected)
    record = record_list[idx]

    # ------------------- Update / Delete Form -------------------
    with st.form("update_delete_form"):
        updated = {}

        # Action selector
        action = st.radio("Action", ["Update", "Delete"])

        if table_name == "cyber_incidents":
            st.subheader("Edit Cyber Incident")
            for field, value in record.items():
                if field == key:
                    updated[field] = st.text_input(field, value, disabled=True)
                elif field == "status":  # Only editable field
                    status_options = ["Open", "In Progress", "Closed", "Resolved", "Investigating"]
                    current_status = value 
                    updated[field] = st.selectbox("Status", status_options, index=status_options.index(current_status))
                else:  # Display-only fields
                    st.text_input(field, value, disabled=True)

        elif table_name == "datasets_metadata":
            st.subheader("Edit Dataset")
            for field, value in record.items():
                if field == key:
                    updated[field] = st.text_input(field, value, disabled=True)
                elif field == "record_count":  # Only editable field
                    updated[field] = st.number_input("Record Count", value=int(value))
                else:  # Display-only fields
                    st.text_input(field, value, disabled=True)


        elif table_name == "it_tickets":
            st.subheader("Edit Ticket")
            for field, value in record.items():
                if field == key:
                    updated[field] = st.text_input(field, value, disabled=True)
                elif field == "status":  # Only editable field
                    status_options = ["Open", "In Progress", "Closed", "Resolved", "Investigating"]
                    current_status = value
                    updated[field] = st.selectbox("Status", status_options, index=status_options.index(current_status))
                else:  # Display-only fields
                    st.text_input(field, value, disabled=True)

        submit = st.form_submit_button("Submit")

    # ------------------- Perform Action -------------------
    if submit:
        try:
            if action == "Update":
                if table_name == "cyber_incidents":
                    update_incident_status(conn, selected, updated.get("status"))
                    st.success(f"Incident '{selected}' updated successfully!")
                elif table_name == "it_tickets":
                    update_ticket(conn, selected, updated.get("status"))
                    st.success(f"Ticket '{selected}' updated successfully!")
                elif table_name == "datasets_metadata":
                    update_dataset(conn, selected, updated.get("record_count"))
                    st.success(f"Dataset '{selected}' updated successfully!")

            elif action == "Delete":
                if table_name == "cyber_incidents":
                    delete_incident(conn, selected)
                elif table_name == "it_tickets":
                    delete_ticket(conn, selected)
                elif table_name == "datasets_metadata":
                    delete_dataset(conn, selected)
                st.success("Record deleted!")

            st.rerun()
        except Exception as e:
            st.error(f"Action failed: {e}")



# ------------------- DATA VISUALIZATION -------------------

def data_visualization(conn, table_name):
    if table_name == "cyber_incidents":
        st.subheader("📊 Cybersecurity Incidents Visualizations")

        df_all = get_all_incidents(conn)
        if df_all.empty:
            st.info("No incident data available for visualization.")
            return
        
    
        col1, col2 = st.columns(2)
        with col1:
            df_type_count = get_incidents_by_type_count(conn)
            fig1 = px.bar(df_type_count, x="incident_type", y="count",
                          color="incident_type", title="Total Incidents by Type")
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            df_high_sev = get_high_severity_by_status(conn)
            if not df_high_sev.empty:
                fig2 = px.pie(df_high_sev, names="status", values="count",
                              title="High Severity Incidents Distribution")
                st.plotly_chart(fig2, use_container_width=True)

        df_many_cases = get_incident_types_with_many_cases(conn, min_count=5)
        if not df_many_cases.empty:
            fig3 = px.bar(df_many_cases, x="incident_type", y="count",
                          color="incident_type", title="Incident Types with >5 Cases")
            st.plotly_chart(fig3, use_container_width=True)

        df_trend = get_incident_trend(conn)
        fig4 = px.line(df_trend, x="incident_type", y="total_incidents",
                       title="Trend of Incidents by Type")
        st.plotly_chart(fig4, use_container_width=True)

        df_unresolved = unresolved_incidents_by_type(conn)
        if not df_unresolved.empty:
            fig5 = px.bar(df_unresolved, x="incident_type", y="unresolved_cases",
                          color="incident_type", title="Unresolved Incidents")
            st.plotly_chart(fig5, use_container_width=True)
        


        st.write("### 🔥 Incident Severity vs Type Heatmap")

        # Pivot data for meaningful visualization
        heatmap_data = df_all.pivot_table(
            values="id",
            index="incident_type",
            columns="severity",
            aggfunc="count",
            fill_value=0
        )

        # Sort severity in logical cybersecurity order
        severity_order = ["Low", "Medium", "High", "Critical"]
        heatmap_data = heatmap_data.reindex(columns=severity_order, fill_value=0)

        # Create heatmap figure
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt="d",
            cmap="coolwarm",    # Better contrast
            linewidths=0.5,
            square=True,
            ax=ax,
            cbar_kws={"label": "Number of incidents"}
        )

        ax.set_title("Incident Severity Distribution Across Attack Types")
        ax.set_xlabel("Severity Level")
        ax.set_ylabel("Incident Type")

        st.pyplot(fig)

        

         # ------------------- Security Metrics -------------------
        threats_detected = len(df_all)  # Total incidents
        vulnerabilities = df_all[df_all["severity"] == "Critical"].shape[0]  # Critical severity count
        open_incidents = df_all[df_all["status"] == "Open"].shape[0]  # Open incidents

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Threats Detected", threats_detected, delta=f"+{threats_detected - 50}")
        with col2:
            st.metric("Vulnerabilities", vulnerabilities, delta=f"-{5}")  # Replace with dynamic delta if needed
        with col3:
            st.metric("Open Incidents", open_incidents, delta=f"+{open_incidents - 2}")

    elif table_name == "it_tickets":
        st.subheader("📊 IT Tickets Visualizations")

    elif table_name == "datasets_metadata":
        st.subheader("📊 Data Science Datasets Visualizations")


    else:
        st.error("Unknown table for visualization.")
