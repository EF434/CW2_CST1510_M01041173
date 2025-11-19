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
    
def get_all_incidents(conn):
    """
    Retrieve all incidents from the database.
    
    TODO: Implement using pandas.read_sql_query()
    
    Returns:
        pandas.DataFrame: All incidents
    """
    # TODO: Use pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
    conn = connect_database()
    df =  pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
    conn.close()
    return df

def update_incident_status(conn, incident_id, new_status):
    """
    Update the status of an incident.
    
    TODO: Implement UPDATE operation.
    """
    # TODO: Write UPDATE SQL: UPDATE cyber_incidents SET status = ? WHERE id = ?
    cursor = conn.cursor()
    update_sql = """
    UPDATE cyber_incidents SET status = ? WHERE id = ?
    """
    # TODO: Execute and commit
    cursor.execute(update_sql, (new_status, incident_id))
    conn.commit()
    # TODO: Return cursor.rowcount
    return cursor.rowcount

def delete_incident(conn, incident_id):
    """
    Delete an incident from the database.
    
    TODO: Implement DELETE operation.
    """
    # TODO: Write DELETE SQL: DELETE FROM cyber_incidents WHERE id = ?
    cursor = conn.cursor()
    delete_sql = """
    DELETE FROM cyber_incidents WHERE id = ?
    """
    # TODO: Execute and commit
    cursor.execute(delete_sql, (incident_id,))
    conn.commit()
    # TODO: Return cursor.rowcount
    return cursor.rowcount




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

# Test: Run analytical queries
conn = connect_database()

print("\n Incidents by Type:")
df_by_type = get_incidents_by_type_count(conn)
print(df_by_type)

print("\n High Severity Incidents by Status:")
df_high_severity = get_high_severity_by_status(conn)
print(df_high_severity)

print("\n Incident Types with Many Cases (>5):")
df_many_cases = get_incident_types_with_many_cases(conn, min_count=5)
print(df_many_cases)

conn.close()