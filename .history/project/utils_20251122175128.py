import pandas as pd
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

# ---- DATABASE CONNECTION (Only once here) ----
conn = connect_database("DATA/intelligence_platform.db")


# ---------- DOMAIN WRAPPER FUNCTIONS ----------
def load_data(domain):
    """Return dataframe, fields and CRUD functions based on the domain."""
    
    if domain == "Cybersecurity":
        

    elif domain == "IT Operations":
        

    elif domain == "Data Science":
        return (
            pd.DataFrame(list_datasets_by_source(conn)),
            ["dataset_name", "source", "last_updated", "size"],
            insert_dataset, update_dataset, delete_dataset
        )
