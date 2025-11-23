import streamlit as st
from utils import view_records, add_new_record, update_delete_record
from incidents import get_all_incidents, insert_incident, update_incident_status, delete_incident
from tickets import get_unresolved_tickets, insert_ticket, update_ticket, delete_ticket
from datasets import get_all_datasets, insert_dataset, update_dataset, delete_dataset

# ---------------- SIDEBAR ----------------
domain_choice = st.sidebar.selectbox("Select Domain", ["Cybersecurity", "IT Operations", "Data Science"])
actions = st.sidebar.multiselect("Select Actions", ["📄 View Records", "➕ Add New Record", "✏ Update / Delete"], default=["📄 View Records"])

# ---------------- LOAD DATA ----------------
df = None
if domain_choice == "Cybersecurity":
    df = get_all_incidents()
elif domain_choice == "IT Operations":
    df = get_unresolved_tickets()
elif domain_choice == "Data Science":
    df = get_all_datasets()

# ---------------- FILTER SETTINGS ----------------
filter_columns = {
    "Cybersecurity": ["severity", "status"],
    "IT Operations": ["priority", "status"],
    "Data Science": []
}

# ---------------- ADD CONFIG ----------------
ADD_CONFIG = {
    "Cybersecurity": {
        "insert_func": insert_incident,
        "form_fields": [
            {"label": "date", "type": "date"},
            {"label": "incident_type", "type": "text"},
            {"label": "severity", "type": "select", "options": ["Low", "Medium", "High", "Critical"]},
            {"label": "status", "type": "select", "options": ["Open", "Investigating", "Resolved", "Closed"]},
            {"label": "description", "type": "textarea"},
            {"label": "reported_by", "type": "text"}
        ]
    },
    "IT Operations": {
        "insert_func": insert_ticket,
        "form_fields": [
            {"label": "ticket_id", "type": "text"},
            {"label": "priority", "type": "select", "options": ["Low","Medium","High","Critical"]},
            {"label": "status", "type": "select", "options": ["Open","In Progress","Resolved","Closed"]},
            {"label": "category", "type": "text"},
            {"label": "subject", "type": "text"},
            {"label": "description", "type": "textarea"},
            {"label": "created_date", "type": "date"},
            {"label": "resolved_date", "type": "date"},
            {"label": "assigned_to", "type": "text"}
        ]
    },
    "Data Science": {
        "insert_func": insert_dataset,
        "form_fields": [
            {"label": "dataset_name", "type": "text"},
            {"label": "source", "type": "text"},
            {"label": "category", "type": "text"},
            {"label": "last_updated", "type": "date"},
            {"label": "record_count", "type": "text"},
            {"label": "file_size_mb", "type": "text"}
        ]
    }
}

# ---------------- ACTION HANDLING ----------------
for action in actions:
    if action == "📄 View Records":
        view_records(domain_choice, df, filter_columns.get(domain_choice))
    elif action == "➕ Add New Record":
        config = ADD_CONFIG.get(domain_choice)
        if config:
            add_new_record(domain_choice, config["insert_func"], config["form_fields"])
    elif action == "✏ Update / Delete":
        mapping = {
            "Cybersecurity": (update_incident_status, delete_incident),
            "IT Operations": (update_ticket, delete_ticket),
            "Data Science": (update_dataset, delete_dataset)
        }
        update_func, delete_func = mapping[domain_choice]
        update_delete_record(domain_choice, df, update_func, delete_func, ADD_CONFIG[domain_choice]["form_fields"])
