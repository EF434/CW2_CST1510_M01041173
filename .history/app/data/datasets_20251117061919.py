# dataset.py

# Import required modules
import pandas as pd
import sqlite3


def insert_incident(conn, date, incident_type, severity, status,
                    description, reported_by, created_at=None):
    """
    Insert a new incident record into the database.

    TODO: Implement this following the style of register_user() and insert_ticket()

    Args:
        conn: Database connection
        date: Date the incident occurred (TEXT)
        incident_type: Type of security or IT incident
        severity: Severity level (Low, Medium, High, Critical)
        status: Current status (Open, In Progress, Resolved, Escalated)
        description: Full details of the incident
        reported_by: Person or system reporting the incident
        created_at: Timestamp (optional)

    Returns:
        int: ID of the inserted record
    """
    try:
        cursor = conn.cursor()

        # SQL insert query
        insert_sql = """
        INSERT INTO dataset
        (date, incident_type, severity, status, description, reported_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(insert_sql, (date, incident_type, severity, status,
                                    description, reported_by, created_at))
        conn.commit()

        print(f"✅ Incident reported by '{reported_by}' inserted successfully.")
        return cursor.lastrowid

    except sqlite3.Error as e:
        print(f"❌ Error inserting incident: {e}")
        return None



def get_all_incidents(conn):
    """
    Retrieve all logged incidents.

    Returns:
        pandas.DataFrame: All incident records
    """
    try:
        df = pd.read_sql_query("SELECT * FROM dataset", conn)
        print(f"📄 Retrieved {len(df)} incidents from the database.")
        return df
    except Exception as e:
        print(f"❌ Error retrieving incidents: {e}")
        return pd.DataFrame()



def update_incident_status(conn, incident_id, new_status):
    """
    Update the status of a specific incident.

    Args:
        conn: Database connection
        incident_id: ID of the record
        new_status: New status string

    Returns:
        int: Number of rows updated
    """
    try:
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE dataset SET status = ? WHERE id = ?",
            (new_status, incident_id)
        )
        conn.commit()

        print(f"🔄 Incident {incident_id} updated to status '{new_status}'")
        return cursor.rowcount

    except Exception as e:
        print(f"❌ Failed to update incident {incident_id}: {e}")
        return 0



def delete_incident(conn, incident_id):
    """
    Delete an incident record.

    Args:
        incident_id: Target record ID
    """
    try:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM dataset WHERE id = ?",
            (incident_id,)
        )
        conn.commit()

        print(f"🗑️ Incident {incident_id} removed successfully.")
        return cursor.rowcount

    except Exception as e:
        print(f"❌ Error deleting incident {incident_id}: {e}")
        return 0



def count_incidents_by_severity(conn):
    """
    Get a summary of incidents by severity.

    Uses GROUP BY & ORDER BY
    """
    query = """
    SELECT severity, COUNT(*) AS count
    FROM dataset
    GROUP BY severity
    ORDER BY count DESC
    """

    return pd.read_sql_query(query, conn)



def get_open_incidents(conn):
    """
    Retrieve unresolved or non-closed incidents.

    Returns:
        pandas.DataFrame
    """
    query = """
    SELECT *
    FROM dataset
    WHERE status NOT IN ('Resolved', 'Closed')
    ORDER BY severity DESC
    """

    return pd.read_sql_query(query, conn)
