# ---------------- ADD CONFIG ----------------
from app.data.incidents import insert_incident
from app.data.tickets import insert_ticket
from app.data.datasets import insert_dataset

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
