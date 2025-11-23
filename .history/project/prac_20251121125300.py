# Import Streamlit and Week 8 functions
import streamlit as st
from app.data.db import connect_database
from app.data.incidents import (
    insert_incident,
    get_all_incidents
)

# Connect to database (Week 8 function)
conn = connect_database('DATA/intelligence_platform.db')

# Page title
st.title("Cyber Incidents Dashboard")

# READ: Display incidents in a beautiful table (Week 8 function + Streamlit UI)
incidents = get_all_incidents(conn) # ← Week 8 function handles SQL
st.dataframe(incidents, use_container_width=True) # ← Streamlit creates UI

# CREATE: Add new incident with a form
with st.form("new_incident"):
# Form inputs (Streamlit widgets)
 title = st.text_input("Incident Title")
 severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
 status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])

# Form submit button
 submitted = st.form_submit_button("Add Incident")

# When form is submitted
if submitted and title:
# Call Week 8 function to insert into database
insert_incident(conn, title, severity, status) # ← Week 8 function!
st.success("✓ Incident added successfully!")
st.rerun() # Refresh the page to show new incident
