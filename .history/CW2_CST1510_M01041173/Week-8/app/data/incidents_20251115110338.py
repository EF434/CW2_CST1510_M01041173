import pandas as pd
from app.data.db import connect_database

def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):
    """
    Insert a new cyber incident into the database.
    
    TODO: Implement this function following the register_user() pattern.
    
    Args:
        conn: Database connection
        date: Incident date (YYYY-MM-DD)
        incident_type: Type of incident
        severity: Severity level
        status: Current status
        description: Incident description
        reported_by: Username of reporter (optional)
        
    Returns:
        int: ID of the inserted incident
    """
    # TODO: Get cursor
    cursor = conn.cursor()
    # TODO: Write INSERT SQL with parameterized query
    insert_sql = """
    INSERT INTO cyber_incidents (date, incident_type, severity, status, description, reported_by)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    # TODO: Execute and commit
    cursor.execute(insert_sql, (date, incident_type, severity, status, description, reported_by))
    conn.commit()
    # TODO: Return cursor.lastrowid
    return cursor.lastrowid
    
def get_all_incidents():
    """Get all incidents as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC",
        conn
    )
    conn.close()
    return df