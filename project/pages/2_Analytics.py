# ------------------- IMPORTS -------------------
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import time
import numpy as np
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

# ------------------- LOGIN CHECK -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("You must be logged in.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()


# ---------- Streamlit Page Config ----------
st.set_page_config(page_title="Wave - Analytics", layout="wide", page_icon="logo.png")

# ------------------- DATABASE -------------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DB_FILE = os.path.join(DATA_DIR, "intelligence_platform.db")

conn = connect_database(DB_FILE)
create_all_tables(conn)

domain = st.sidebar.selectbox("Select Domain", ["Cybersecurity", "IT Operations", "Data Science"])

# Initilize global variables
df_incidents = get_all_incidents(conn)
df_datasets = get_all_datasets(conn)
df_tickets = get_all_tickets(conn)


# ------------------- VIEW RECORDS -------------------
def view_records(conn, domain):
    st.markdown(
    """
    <style>
    .table-header {font: bold 28px "Segoe UI", Roboto, sans-serif; color:#0b3d91; border-bottom:3px solid #ff4b4b; margin-bottom:10px;}
    table {border-collapse:collapse; width:100%;}
    th {background:#0b3d91; color:#fff; padding:8px; text-align:left;}
    td {padding:6px; border-bottom:1px solid #ddd;}
    tr:hover {background:#f1f1f1;}
    </style>
    """,
    unsafe_allow_html=True
    )

    # ---------------- Cybersecurity ----------------
    if domain == "Cybersecurity":
        st.markdown('<div class="table-header">🔒 Cyber Incidents</div>', unsafe_allow_html=True)

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

        filtered_df = df_incidents[
            df_incidents["severity"].isin(severity_filter) &
            df_incidents["status"].isin(status_filter)   # check this
        ]

        st.caption(f"{len(filtered_df)} incidents after filtering.")
        with st.expander(" Filtered Incidents"):
            st.dataframe(filtered_df, use_container_width=True)

    # ---------------- IT Operations ----------------
    elif domain == "IT Operations":
        st.markdown('<div class="table-header">💻 IT Tickets</div>', unsafe_allow_html=True)

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

        filtered_df = df_tickets[
            df_tickets["priority"].isin(priority_filter) &
            df_tickets["status"].isin(status_filter)
        ]


        st.caption(f"Showing {len(filtered_df)} tickets after filtering.")
        with st.expander("See Filtered Tickets"):
            st.dataframe(filtered_df, use_container_width=True, height=600)

    # ---------------- Data Science ----------------
    elif domain == "Data Science":
        st.markdown('<div class="table-header">📊 Data Science Datasets</div>', unsafe_allow_html=True)

        df_datasets["last_updated"] = pd.to_datetime(df_datasets["last_updated"], errors="coerce")

        category_filter = st.multiselect(
            "Category",
            options=df_datasets["category"].unique(),
            default=df_datasets["category"].unique()
        )
        min_records = int(df_datasets["record_count"].min())
        max_records = int(df_datasets["record_count"].max())

        record_range = st.slider(
            "Record Count Range",
            min_value=min_records,
            max_value=max_records,
            value=(min_records, max_records)
        )

        filtered_df = df_datasets[
            df_datasets["category"].isin(category_filter) &
            df_datasets["record_count"].between(record_range[0], record_range[1])
        ]

        st.caption(f"Showing {len(filtered_df)} datasets after filtering.")
        with st.expander("See Filtered Datasets"):
            st.dataframe(filtered_df, use_container_width=True, height=600)

    else:
        st.error("Unknown domain selected.")


def domain_visulization():
    if domain == "Cybersecurity":

        # Define tabs
        tab1, tab2, tab3 = st.tabs(["Overview", "Trend Line", "Other Charts"])

        # ----------------- TAB 1: KPIs + Threat Type Bar -----------------
        with tab1:

            df_types = get_incidents_by_type_count(conn)

            # Bar chart of threat types
            st.markdown("<h3 style='text-align: center;'>Threat Types Overview</h3>", unsafe_allow_html=True)

            chart = (
                alt.Chart(df_types)
                .mark_bar(cornerRadiusTopLeft=12, cornerRadiusTopRight=12)
                .encode(
                    x=alt.X(
                        "incident_type:N",
                        axis=alt.Axis(labelAngle=0, title="Threat Type"),
                        sort=None
                    ),
                    y=alt.Y("count:Q", title="Incident Count"),
                    color=alt.Color("incident_type:N", legend=None),
                    tooltip=["incident_type", "count"]
                )
                .properties(width=1000, height=450)
            )

            text = chart.mark_text(
                dy=-12,
                fontSize=14,
                fontWeight="bold"
            ).encode(text="count:Q")

            st.altair_chart(chart + text, use_container_width=True)


            st.markdown("<h3 style='text-align: center;'> Cybersecurity Overview / KPIs</h3>", unsafe_allow_html=True)


            # KPI metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                total_threats = len(df_incidents)
                st.metric("Threats Detected", total_threats)

            with col2:
                vuln_count = df_incidents[df_incidents["severity"].isin(["Critical", "High"])].shape[0]
                st.metric("High-Risk Vulnerabilities", vuln_count)

            with col3:
                active_incidents = df_incidents[df_incidents["status"].isin(["Open", "Investigating"])].shape[0]
                st.metric("Active Incidents", active_incidents)

        # ----------------- TAB 2: Trend Line Chart -----------------
        with tab2:
            st.subheader("📈 Monthly Trend for Multiple Threat Types")

            # 1️⃣ Ensure 'date' is datetime
            df_incidents['date'] = pd.to_datetime(df_incidents['date'])

            # 2️⃣ Aggregate monthly counts per incident type
            df_trend = df_incidents.groupby([pd.Grouper(key='date', freq='M'), 'incident_type']).size().reset_index(name='count')

            # 3️⃣ Format month nicely
            df_trend['month'] = df_trend['date'].dt.strftime('%Y-%m')

            # 4️⃣ Plot line chart with Plotly Express
            fig = px.line(
                df_trend,
                x='month',
                y='count',
                color='incident_type',
                markers=True,
                labels={'month': 'Month', 'count': 'Incident Count', 'incident_type': 'Threat Type'},
                title='📈 Monthly Trend of Incidents'
            )

            # 5️⃣ Display chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)


        # ----------------- TAB 3: Other Charts -----------------
        with tab3:


            # 1️⃣ Get unresolved incident counts by type
            df_unresolved = unresolved_incidents_by_type(conn)

            # 2️⃣ Get all incidents to get monthly info
            df_all = get_all_incidents(conn)
            df_all['date'] = pd.to_datetime(df_all['date'])

            # 3️⃣ Merge to get monthly counts only for unresolved types
            df_unresolved_types = df_all[df_all['status'] != 'Resolved']
            df_unresolved_types = df_unresolved_types[df_unresolved_types['incident_type'].isin(df_unresolved['incident_type'])]

            # 4️⃣ Aggregate by month and type
            df_heat = (
                df_unresolved_types
                .groupby([pd.Grouper(key='date', freq='M'), 'incident_type'])
                .size()
                .reset_index(name='count')
            )

            # 5️⃣ Format month nicely
            df_heat['month'] = df_heat['date'].dt.strftime('%Y-%m')

            # 6️⃣ Pivot for heatmap
            df_pivot = df_heat.pivot(index='incident_type', columns='month', values='count').fillna(0)

            # 7️⃣ Plot heatmap
            fig = px.imshow(
                df_pivot,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='YlOrRd',
                labels=dict(x="Month", y="Incident Type", color="Unresolved Count"),
                title="🔥 Heatmap of Unresolved Incidents per Month and Threat Type"
            )

            st.plotly_chart(fig, use_container_width=True)

            
    elif domain == "IT Operations":
        pass
        # st.metric() for system health
        #  Line charts for resource trends
        # Area charts for network traffic
        # Status indicators for services

        # Built-in Charts: st.line_chart(), st.bar_chart(), st.area_chart()
        # st.empty() and loops for live dashboards


    elif domain == "Data Science":
        # Load all datasets
        df = get_all_datasets(conn)

        # ------------------ Metrics ------------------
        # Aggregate some simple numbers
        total_datasets = len(df)
        total_records = df['record_count'].sum()
        total_size = df['file_size_mb'].sum()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Datasets", total_datasets)

        with col2:
            st.metric("Total Records", f"{total_records:,}")

        with col3:
            st.metric("Total Size (MB)", round(total_size, 1))


        # ----------------- Prepare line chart -----------------
        # Convert last_updated to datetime
        df['last_updated'] = pd.to_datetime(df['last_updated'])

        # Sort by date
        df_sorted = df.sort_values('last_updated')

        # Build a simple DataFrame for trends
        usage = pd.DataFrame({
            "Date": df_sorted['last_updated'],
            "Records": df_sorted['record_count'].cumsum(),
            "Size_MB": df_sorted['file_size_mb'].cumsum()
        })

        # ----------------- Display line chart -----------------
        st.subheader("Dataset Resource Trends Over Time")
        st.line_chart(usage.set_index("Date"))

        # Scatter plot
                # -------------------------------------------------------
        # 3️⃣ Select only numeric columns for correlation
        # -------------------------------------------------------
        numeric_df = df[["record_count", "file_size_mb"]]

        # -------------------------------------------------------
        # 4️⃣ Scatter Plot + labels
        # -------------------------------------------------------
        plt.figure(figsize=(7, 5))
        plt.scatter(df["record_count"], df["file_size_mb"])
        plt.title("Scatter Plot: Record Count vs File Size (MB)")
        plt.xlabel("Record Count")
        plt.ylabel("File Size (MB)")

        # Add text labels beside points
        for i, row in df.iterrows():
            plt.annotate(row["dataset_name"], (row["record_count"], row["file_size_mb"]),
                        textcoords="offset points", xytext=(5, 5), fontsize=8)

        plt.tight_layout()
        plt.show()

        # -------------------------------------------------------
        # 5️⃣ Optional: Correlation Pairplot
        # -------------------------------------------------------
        sns.pairplot(numeric_df, kind="scatter")
        plt.suptitle("Dataset Correlation Scatter Matrix", y=1.02)
        plt.show()


        # ---------------------- SAMPLE DATA ----------------------
        # If you're loading from database use:
        # df = get_all_datasets(conn)
        # otherwise using manual inline data for now:

        data = {
            "dataset_name": [
                "Threat Intel Logs Q1 2025",
                "Corporate Network Logs Apr-May 2025",
                "Endpoint Security Events Mar 2025"
            ],
            "category": ["Threat Intelligence", "Network Logs", "Endpoint Monitoring"],
            "source": ["External Threat Feed", "Internal SIEM", "Internal EDR"],
            "last_updated": ["2025-11-01", "2025-10-28", "2025-10-30"],
            "record_count": [250000, 1500000, 500000],
            "file_size_mb": [120.5, 950.0, 320.2]
        }

        df = pd.DataFrame(data)

        # ---------------------- SCATTER PLOTS ----------------------

        # Select numeric data
        numeric_df = df[["record_count", "file_size_mb"]]

        # 🔹 Pairplot for correlations
        sns.pairplot(numeric_df, kind="scatter")
        plt.suptitle("Correlation Scatter Matrix", y=1.02, fontsize=14)
        plt.show()

        # 🔹 Individual scatter plot: record_count vs file_size_mb
        plt.figure(figsize=(6,4))
        plt.scatter(df["record_count"], df["file_size_mb"])
        plt.title("Record Count vs File Size (MB)")
        plt.xlabel("Record Count")
        plt.ylabel("File Size (MB)")

        # Add dataset labels to scatter points for context
        for i, row in df.iterrows():
            plt.annotate(row["dataset_name"], (row["record_count"], row["file_size_mb"]),
                        textcoords="offset points", xytext=(5,5), fontsize=8)

        plt.tight_layout()
        plt.show()


        # confusion matrix Heatmap

    else:
        pass
    
domain_visulization()
