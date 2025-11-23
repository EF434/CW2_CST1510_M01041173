import streamlit as st
import pandas as pd
from pathlib import Path
from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident

# ----------------------------
# Database connection
# ----------------------------
fromapp.data.dbimport connect_database

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
    
    # Display incidents table
    df_incidents = get_all_incidents(conn)
    if not df_incidents.empty:
        if "date" in df_incidents.columns:
            df_incidents["date"] = pd.to_datetime(df_incidents["date"]).dt.date

        def highlight_severity(val):
            color = 'red' if val in ['High', 'Critical'] else ''
            return f'background-color: {color}'
        
        st.dataframe(df_incidents.style.applymap(highlight_severity, subset=['severity']),
                     use_container_width=True)
    else:
        st.info("No incidents found.")

    # Add new incident
    st.subheader("➕ Add New Incident")
    with st.form("new_incident_form"):
        title = st.text_input("Incident Title")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        submitted = st.form_submit_button("Add Incident")
        if submitted:
            if title.strip():
                insert_incident(conn, title.strip(), severity, status)
                st.success("✓ Incident added successfully!")
                st.experimental_rerun()
            else:
                st.error("Title cannot be empty!")

    # Visualizations
    st.subheader("📊 Threat Distribution")
    threat_data = {"Malware": 89, "Phishing": 67, "DDoS": 45, "Intrusion": 46}
    st.bar_chart(pd.DataFrame.from_dict(threat_data, orient='index', columns=['Count']))

elif selected_domain == "Data Science":
    st.subheader("📊 Data Science Records")
    
    if "ds_records" not in st.session_state:
        st.session_state.ds_records = []

    # Display table
    if st.session_state.ds_records:
        st.dataframe(pd.DataFrame(st.session_state.ds_records), use_container_width=True)
    else:
        st.info("No Data Science records found.")

    # Add new record
    with st.form("ds_form"):
        name = st.text_input("Name")
        metric = st.number_input("Metric Value")
        submitted = st.form_submit_button("Add Record")
        if submitted:
            st.session_state.ds_records.append({"Name": name, "Metric": metric})
            st.success("Record added!")
            st.experimental_rerun()

    # Visualizations
    if st.session_state.ds_records:
        df_ds = pd.DataFrame(st.session_state.ds_records)
        st.bar_chart(df_ds.set_index("Name"))

elif selected_domain == "IT Operations":
    st.subheader("⚙️ IT Operations Tickets")
    
    if "it_records" not in st.session_state:
        st.session_state.it_records = []

    # Display table
    if st.session_state.it_records:
        st.dataframe(pd.DataFrame(st.session_state.it_records), use_container_width=True)
    else:
        st.info("No IT Operations records found.")

    # Add new ticket
    with st.form("it_form"):
        ticket = st.text_input("Ticket ID")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        submitted = st.form_submit_button("Add Ticket")
        if submitted:
            st.session_state.it_records.append({"Ticket": ticket, "Priority": priority})
            st.success("Ticket added!")
            st.experimental_rerun()

    # Metrics
    col1, col2 = st.columns(2)
    col1.metric("Open Tickets", len([t for t in st.session_state.it_records if t["Priority"]=="High"]))
    col2.metric("Total Tickets", len(st.session_state.it_records))
