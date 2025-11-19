"""
incidents.py - provides helper managing cybersecurity incident records stored in the database.

Provides:
- Function to insert a new incident
- Function to retrieve existing incidents (all or filtered)
- Functions to update or delete incident records
- Aggregation helpers for reporting and analysis

"""

# Import required modules
import pandas as pd
import sqlite3
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
    try:
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
    except sqlite3.Error as e:
        print(f"Error inserting incident: {e}")
        return None
    
    
def get_all_incidents(conn):
    """
    Retrieve all incidents from the database.
    
    TODO: Implement using pandas.read_sql_query()
    
    Returns:
        pandas.DataFrame: All incidents
    """
    # TODO: Use pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
    try:
        df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
        print(f"✅ Retrieved {len(df)} incidents from the database.")
        return df
    except Exception as e:
        print(f"Error retrieving incidents: {e}")
        return pd.DataFrame()
    

def update_incident_status(conn, incident_id, new_status):
    """
    Update the status of an incident.
    
    TODO: Implement UPDATE operation.
    """
    # TODO: Write UPDATE SQL: UPDATE cyber_incidents SET status = ? WHERE id = ?
    try:
        # Get cursor
        cursor = conn.cursor()
        # TODO: Execute and commit
        cursor.execute(
            "UPDATE cyber_incidents SET status = ? WHERE id = ?",
            (new_status, incident_id)
        )
        conn.commit()
        print(f"✅ Successfully updated incident {incident_id} to '{new_status}'")

        # TODO: Return cursor.rowcount
        return cursor.rowcount
    
    except Exception as e:
        print(f"❌ Failed to update incident {incident_id}: {e}")
        return 0
 

def delete_incident(conn, incident_id):
    """
    Delete an incident from the database.
    
    TODO: Implement DELETE operation.
    """
    # TODO: Write DELETE SQL: DELETE FROM cyber_incidents WHERE id = ?
    try:
        # Get cursor
        cursor = conn.cursor()
        # TODO: Execute and commit
        cursor.execute(
            "DELETE FROM cyber_incidents WHERE id = ?",
            (incident_id,)
        )
        conn.commit()
        # TODO: Return cursor.rowcount
        return cursor.rowcount
    
    except Exception as e:
        print(f"Error! Incident {incident_id} deletion failed: {e}")
        return 0
    

def get_incidents_by_type_count(conn):
    """
    Count incidents by type.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_severity_by_status(conn):
    """
    Count high severity incidents by status.
    Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_incident_types_with_many_cases(conn, min_count=5):
    """
    Find incident types with more than min_count cases.
    Uses: SELECT, FROM, GROUP BY, HAVING, ORDER BY
    """
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df

