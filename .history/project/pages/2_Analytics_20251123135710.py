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
        
        # Fetch data
        df_all = get_all_incidents(conn)
        if df_all.empty:
            st.info("No incident data available for visualization.")
            return
        
        # ---------------- Sidebar Filters ----------------
        st.sidebar.markdown("### Filter Incidents")
        severity_filter = st.sidebar.multiselect(
            "Select Severity",
            options=["Low", "Medium", "High", "Critical"],
            default=["Low", "Medium", "High", "Critical"]
        )
        status_filter = st.sidebar.multiselect(
            "Select Status",
            options=["Open", "Investigating", "Resolved", "Closed"],
            default=["Open", "Investigating", "Resolved", "Closed"]
        )
        
        df_filtered = df_all[
            df_all["severity"].isin(severity_filter) &
            df_all["status"].isin(status_filter)
        ]
        
        st.caption(f"Showing {len(df_filtered)} records after filtering.")
        
        # ---------------- Metrics ----------------
        threats_detected = len(df_filtered)
        vulnerabilities = df_filtered[df_filtered["severity"] == "Critical"].shape[0]
        open_incidents = df_filtered[df_filtered["status"] == "Open"].shape[0]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Threats Detected", threats_detected, delta=f"+{threats_detected - 50}")
        col2.metric("Critical Vulnerabilities", vulnerabilities, delta=f"{vulnerabilities - 5}")
        col3.metric("Open Incidents", open_incidents, delta=f"+{open_incidents - 2}")
        
        # ---------------- Tabs for Charts ----------------
        tab1, tab2, tab3, tab4 = st.tabs(["Incidents by Type", "High Severity Distribution", "Trend & Unresolved", "Severity Heatmap"])
        
        with tab1:
            df_type_count = get_incidents_by_type_count(conn).sort_values("count", ascending=False)
            fig1 = px.bar(df_type_count, x="incident_type", y="count", color="incident_type",
                          title="Total Incidents by Type", text="count")
            st.plotly_chart(fig1, use_container_width=True)
            
        with tab2:
            df_high_sev = get_high_severity_by_status(conn)
            if not df_high_sev.empty:
                fig2 = px.pie(df_high_sev, names="status", values="count",
                              title="High Severity Incidents Distribution", hole=0.3)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No high severity incidents found.")
        
        with tab3:
            df_trend = get_incident_trend(conn)
            fig3 = px.line(df_trend, x="incident_type", y="total_incidents",
                           title="Trend of Incidents by Type", markers=True)
            st.plotly_chart(fig3, use_container_width=True)
            
            df_unresolved = unresolved_incidents_by_type(conn)
            if not df_unresolved.empty:
                fig4 = px.bar(df_unresolved, x="incident_type", y="unresolved_cases",
                              color="incident_type", title="Unresolved Incidents")
                st.plotly_chart(fig4, use_container_width=True)
        
        with tab4:
            # Heatmap
            heatmap_data = df_filtered.pivot_table(
                values="id",
                index="incident_type",
                columns="severity",
                aggfunc="count",
                fill_value=0
            )
            severity_order = ["Low", "Medium", "High", "Critical"]
            heatmap_data = heatmap_data.reindex(columns=severity_order, fill_value=0)
            
            fig5 = px.imshow(
                heatmap_data,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                aspect="auto",
                labels=dict(x="Severity", y="Incident Type", color="Count")
            )
            fig5.update_layout(title="Incident Severity Distribution Across Types")
            st.plotly_chart(fig5, use_container_width=True)
    
    elif domain == "Data Science":
        st.subheader("📊 Data Science Datasets Visualizations")
        df = get_all_datasets(conn)
        if df.empty:
            st.info("No dataset metadata available for visualization.")
            return
        st.write("Implement dataset charts here...")  # Placeholder
        
    else:
        st.error("Unknown domain selected.")


# ------------------- RUN VISUALIZATION -------------------
visualize_domain(domain)