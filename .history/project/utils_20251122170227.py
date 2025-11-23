import streamlit as st
import pandas as pd

# ----------------- DATABASE CONNECTION -----------------
from app.data.db import connect_database
from app.data.incidents import (
    get_all_incidents, insert_incident,
    update_incident_status, delete_incident
)
from app.data.tickets import (
    get_unresolved_tickets, insert_ticket,
    update_ticket, delete_ticket
)
from app.data.datasets import (
    list_datasets_by_source, insert_dataset,
    update_dataset, delete_dataset
)

conn = connect_database("DATA/intelligence_platform.db")

st.title("🧠 Simple Intelligence Platform")


# ----------------- SELECT DOMAIN -----------------
domain = st.selectbox("Choose Area", ["Cybersecurity", "IT Operations", "Data Science"])


# ----------------- LOAD DATA BASED ON DOMAIN -----------------
if domain == "Cybersecurity":
    df = pd.DataFrame(get_all_incidents(conn))
    fields = ["title", "severity", "status", "description", "reported_by"]
    insert_func = insert_incident
    update_func = update_incident_status
    delete_func = delete_incident

elif domain == "IT Operations":
    df = pd.DataFrame(get_unresolved_tickets(conn))
    fields = ["title", "priority", "status", "assigned_to"]
    insert_func = insert_ticket
    update_func = update_ticket
    delete_func = delete_ticket

elif domain == "Data Science":
    df = pd.DataFrame(list_datasets_by_source(conn))
    fields = ["dataset_name", "source", "last_updated", "size"]
    insert_func = insert_dataset
    update_func = update_dataset
    delete_func = delete_dataset


# ----------------- VIEW DATA -----------------
st.subheader(f"📄 {domain} Records")

if df.empty:
    st.info("No records found.")
else:
    st.dataframe(df, use_container_width=True)


# ----------------- ADD NEW RECORD -----------------
st.subheader(f"➕ Add New {domain} Record")

with st.form("add_form"):
    inputs = {field: st.text_input(field.replace("_", " ").title()) for field in fields}

    if st.form_submit_button("Add"):
        insert_func(conn, **inputs)
        st.success("Record added!")
        st.rerun()


# ----------------- UPDATE RECORD -----------------
if not df.empty:
    st.subheader(f"✏ Update {domain} Record")

    record_id = st.selectbox("Select ID to Update", df["id"])
    record = df[df["id"] == record_id].iloc[0]

    with st.form("update_form"):
        updated = {
            field: st.text_input(field.replace("_", " ").title(), value=str(record[field]))
            for field in fields
        }

        if st.form_submit_button("Update"):
            update_func(conn, record_id, **updated)
            st.success("Updated successfully!")
            st.rerun()


# ----------------- DELETE RECORD -----------------
if not df.empty:
    st.subheader(f"❌ Delete Record")

    delete_id = st.selectbox("Select ID to Delete", df["id"])

    if st.button("Delete Record", type="primary"):
        delete_func(conn, delete_id)
        st.success("Record deleted!")
        st.rerun()
