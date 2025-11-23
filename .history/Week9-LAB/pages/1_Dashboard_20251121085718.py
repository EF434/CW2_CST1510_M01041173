import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import sys
from pathlib import Path
import datetime                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         

# ----------------------------
# Database connection
# ----------------------------
import os

DATA_DIR = Path("app/data")  # Adjust if your data folder is somewhere else
DB_PATH = DATA_DIR / "intelligence_platform.db"

# Make sure the directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Create the connection
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row  # Optional: to access columns by name
 
from app.data.incidents import (
    insert_incident,
    get_all_incidents,
    update_incident_status,
    delete_incident,
    get_incidents_by_type_count,
    get_high_severity_by_status,
    get_incident_types_with_many_cases
)
from app.data.tickets import (
    insert_ticket,
    update_ticket,
    delete_ticket,
    get_unresolved_tickets
    
)

from app.data.datasets import (
    insert_dataset,
    update_dataset,
    delete_dataset,
    get_top_recent_updates
    
)

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Dashboard", page_icon="logo.png", layout="wide")

# ----------------------------
# Session guard
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.title("📊 Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")



# ----------------------------
# Domain selection
# ----------------------------
domains = ["Cybersecurity", "IT Operations", "Data Science"]
selected_domain = st.sidebar.selectbox("Select Your Domain", domains)
st.markdown(
    f"<h1 style='text-align: center;'>🌐 {selected_domain} Dashboard</h1>",
    unsafe_allow_html=True
)

# ----------------------------
# Sidebar navigation (outside domain-specific logic)
# ----------------------------
menu = ["➕ Add Item", "📋 View / Edit Database", "📊 Analytics & Visualizations"]
choice = st.sidebar.radio("Navigation", menu)

# ----------------------------
# Domain-specific actions
# ----------------------------
if selected_domain == "Cybersecurity":
    st.subheader("🛡️ Cyber Incident Management")

    if choice == menu[0]:
        st.subheader("Add a New Incident")
        with st.form("incident_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Incident Date")
                incident_type = st.selectbox(
                    "Incident Type", ["Malware", "Phishing", "DDoS", "Ransomware"]
                )
            with col2:
                severity = st.selectbox("Severity", ["Low", "Medium", "High"])
                status = st.selectbox("Status", ["Open", "Investigating", "Resolved"])

            description = st.text_area("Incident Description")
            reported_by = st.text_input("Reported By (Username)")

            submitted = st.form_submit_button("Add Incident")

            if submitted:
                # Convert date to string in YYYY-MM-DD format
                date_str = date_input.strftime("%Y-%m-%d")
            
            row_id = insert_incident(
                conn,
                date_str,
                incident_type,
                severity,
                status,
                description,
                reported_by if reported_by.strip() else None
            )
            
            if row_id:
                st.success(f"Incident #{row_id} added successfully!")
            else:
                st.error("❌ Failed to add incident. Check console for errors.")

    elif choice == menu[1]:
        st.subheader("Incident Records")
        df = get_all_incidents(conn)
        if df.empty:
            st.info("No incident records found.")
        else:
            st.dataframe(df, use_container_width=True)
            st.write("---")
            st.subheader("✏️ Update / ❌ Delete Incident")
            selected_id = st.number_input("Incident ID", min_value=1, step=1)
            col1, col2 = st.columns(2)
            with col1:
                new_status = st.selectbox("Update Status", ["Open", "Investigating", "Resolved"])
                if st.button("Update Status"):
                    result = update_incident_status(conn, selected_id, new_status)
                    if result:
                        st.success(f"Updated incident {selected_id} successfully!")
                    else:
                        st.error("Failed to update incident.")
            with col2:
                if st.button("Delete Incident"):
                    result = delete_incident(conn, selected_id)
                    if result:
                        st.warning(f"Incident {selected_id} deleted.")
                    else:
                        st.error("Error deleting incident.")

    elif choice == menu[2]:
        st.subheader("📈 Data Insights & Trends")
        incidents_df = get_all_incidents(conn)
        if incidents_df.empty:
            st.info("No incidents available for visualization.")
        else:
            type_df = get_incidents_by_type_count(conn)
            fig1 = px.bar(type_df, x="incident_type", y="count", title="Incident Frequency by Type")
            st.plotly_chart(fig1, use_container_width=True)

            severity_df = get_high_severity_by_status(conn)
            fig2 = px.pie(severity_df, values="count", names="status", title="High Severity Incidents by Status")
            st.plotly_chart(fig2, use_container_width=True)

            if "date" in incidents_df.columns:
                incidents_df["date"] = pd.to_datetime(incidents_df["date"])
                trend = incidents_df.groupby("date").size().reset_index(name="count")
                fig3 = px.line(trend, x="date", y="count", title="📅 Incident Timeline Trend")
                st.plotly_chart(fig3, use_container_width=True)

            st.write("📌 Incident types with more than 5 reported cases:")
            st.dataframe(get_incident_types_with_many_cases(conn), use_container_width=True)

elif selected_domain == "IT OPERATIONS":
    st.subheader("⚙️ IT Operations Dashboard")

    # Add Ticket
    if choice == "➕ Add Item":
        st.subheader("Add a New Ticket")
        with st.form("ticket_form"):
            ticket_id = st.text_input("Ticket ID")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            status = st.selectbox("Status", ["Pending", "In Progress", "Closed"])
            category = st.text_input("Category (Technical, Billing, etc.)")
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            assigned_to = st.text_input("Assigned To")
            created_date = st.date_input("Created Date", datetime.today())
            submitted = st.form_submit_button("Add Ticket")
            if submitted:
                row_id = insert_ticket(
                    conn, ticket_id, priority, status, category, subject, description,
                    str(created_date), None, assigned_to
                )
                if row_id:
                    st.success(f"Ticket '{ticket_id}' added successfully!")
                else:
                    st.error(f"Failed to add ticket '{ticket_id}'.")

    # View / Update / Delete Tickets
    elif choice == "📋 View / Edit Database":
        st.subheader("View / Edit Tickets")
        df = get_unresolved_tickets(conn)
        if df.empty:
            st.info("No unresolved tickets found.")
        else:
            st.dataframe(df, use_container_width=True)
            st.write("---")
            st.subheader("✏️ Update / ❌ Delete Ticket")
            selected_ticket_id = st.text_input("Enter Ticket ID to Update/Delete")
            col1, col2 = st.columns(2)

            with col1:
                new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Closed"])
                if st.button("Update Status"):
                    updated_rows = update_ticket(conn, selected_ticket_id, new_status)
                    if updated_rows:
                        st.success(f"Ticket '{selected_ticket_id}' updated successfully!")
                    else:
                        st.error(f"Failed to update ticket '{selected_ticket_id}'.")

            with col2:
                if st.button("Delete Ticket"):
                    deleted_rows = delete_ticket(conn, selected_ticket_id)
                    if deleted_rows:
                        st.warning(f"Ticket '{selected_ticket_id}' deleted successfully.")
                    else:
                        st.error(f"Failed to delete ticket '{selected_ticket_id}'.")

    # Analytics / Visualizations
    elif choice == "📊 Analytics & Visualizations":
        st.subheader("📊 Ticket Analytics")
        df_all = pd.read_sql_query("SELECT * FROM it_tickets", conn)
        if df_all.empty:
            st.info("No tickets available for analytics.")
        else:
            # Tickets by priority
            priority_count = df_all.groupby("priority").size().reset_index(name="count")
            st.plotly_chart(
                px.bar(priority_count, x="priority", y="count", color="priority", title="Tickets by Priority"),
                use_container_width=True
            )

            # Tickets by status
            status_count = df_all.groupby("status").size().reset_index(name="count")
            st.plotly_chart(
                px.pie(status_count, names="status", values="count", title="Tickets by Status"),
                use_container_width=True
            )

            # Unresolved tickets
            st.write("📌 Unresolved Tickets:")
            st.dataframe(get_unresolved_tickets(conn), use_container_width=True)


elif selected_domain == "Data Science":
    st.subheader("📊 Data Science Dashboard")
    st.info(f"Selected menu: {choice}")
    st.info("Features for Data Science will go here.")
