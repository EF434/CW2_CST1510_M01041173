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


# ------------------- VIEW RECORDS -------------------
def view_records(conn, table_name):
    st.markdown(
            """
            <style>
            .table-header {
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
            """,
            unsafe_allow_html=True
        )

# ------------------- VIEW RECORDS -------------------
def view_records(conn, table_name):
    if table_name == "cyber_incidents":
        df = get_all_incidents(conn)

        st.markdown('<div class="cyber-sub">🔒 Cyber Incidents</div>', unsafe_allow_html=True)


        # Filters above table
        severity_filter = st.multiselect(
            "Select Severity",
            ["Low", "Medium", "High", "Critical"],
            default=["Low", "Medium", "High", "Critical"]
        )

        status_filter = st.multiselect(
            "Select Status",
            ["Open", "Investigating", "Resolved", "Closed"],
            default=["Open", "Investigating", "Resolved", "Closed"]
        )

        # Apply filters
        filtered_df = df[
            df["severity"].isin(severity_filter) &
            df["status"].isin(status_filter)
        ]

    elif table_name == "it_tickets":
        df = get_all_tickets(conn)
        st.markdown('<div class="table-header">💻 IT Tickets</div>', unsafe_allow_html=True)

        # Filters above table
        priority_filter = st.multiselect(
            "Select Priority",
            ["Low", "Medium", "High", "Critical"],
            default=["Low", "Medium", "High", "Critical"]
        )

        status_filter = st.multiselect(
            "Select Status",
            ["Open", "Investigating", "Resolved", "Closed"],
            default=["Open", "Investigating", "Resolved", "Closed"]
        )

        # Apply filters
        filtered_df = df[
            df["priority"].isin(priority_filter) &
            df["status"].isin(status_filter)
        ]

    elif table_name == "datasets_metadata":
        df = get_all_datasets(conn)
        st.markdown('<div class="table-header">📊 Data Science Datasets</div>', unsafe_allow_html=True)

        # Convert last_updated to datetime
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")

        # Filters above table
        department = st.multiselect(
            "Category",
            options=df["category"].unique(),
            default=df["category"].unique()
        )

        min_value = int(df["record_count"].min())
        max_value = int(df["record_count"].max())

        record_count = st.slider(
            "Record Count Range",
            min_value=min_value,
            max_value=max_value,
            value=(min_value, max_value)  # Default range selects all
        )

        # Apply filters
        filtered_df = df[
            df["category"].isin(department) &
            df["record_count"].between(record_count[0], record_count[1])
        ]

    else:
        st.error("Unknown table")
        return

    # Display filtered data
    st.caption(f"Showing {len(filtered_df)} records after filtering.")
    with st.expander("See Filtered Data"):
        st.dataframe(filtered_df, use_container_width=True)
        
# ------------------- DATA VISUALIZATION -------------------
def visualize_domain(domain):
    if domain == "Cybersecurity":
        st.subheader("📊 Cybersecurity Incidents Visualizations")

        df_all = get_all_incidents(conn)
        if df_all.empty:
            st.info("No incident data available for visualization.")
            return
        
    
        # ---------------- Tabs for Charts ----------------
        tab1, tab2, tab3, tab4 = st.tabs(["Incidents by Type", "High Severity Distribution", "Trend & Unresolved", "Severity Heatmap"])
        with tab1:
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

    elif domain == "Data Science":
        st.subheader("📊 Data Science Datasets Visualizations")
        df = get_all_datasets(conn)
        if df.empty:
            st.info("No dataset metadata available for visualization.")
            return
        st.write("Implement dataset charts here...")  # e.g., record count distribution, file size, sources

    else:
        st.error("Unknown domain selected.")

# ------------------- RUN VISUALIZATION -------------------
visualize_domain(domain)