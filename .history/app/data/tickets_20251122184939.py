# tickets.py

# Import required modules
import pandas as pd
import sqlite3


def insert_ticket(conn, ticket_id, priority, status, category, subject, description,
                  created_date=None, resolved_date=None, assigned_to=None):
    """
    Insert a new IT ticket into the database.


    Args:
        conn: Database connection
        ticket_id: Unique ID for ticket (TEXT)
        priority: Priority level (e.g. High, Medium)
        status: Current status (e.g. Pending, Closed)
        category: Type of issue ( Technica, Billing, Refund etc.)
        subject: Short title 
        description: Long ticket message
        created_date: Ticket created date 
        resolved_date: Ticket resolved date (optional)
        assigned_to: Support team category  

    Returns:
        int: ID of the inserted ticket
    """
    try:
        # Get cursor
        cursor = conn.cursor()
        # Write INSERT SQL query
        insert_sql = """
        INSERT INTO it_tickets 
        (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # TODO: Execute and commit  
        cursor.execute(insert_sql, (ticket_id, priority, status, category, subject,
                                    description, created_date, resolved_date, assigned_to))
        conn.commit()

        # Return cursor.lastrowid (return row)
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        print(f"⚠️ Ticket with ID '{ticket_id}' already exists. Skipping...")
        return None

    except sqlite3.Error as e:
        print(f"Error inserting IT ticket: {e}")
        return None


# 🌟 Retrieve all tickets from the database 
def get_all_tickets(conn):
    """
    Get all tickets from the database.
    
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
    
def update_ticket(conn, ticket_id, new_status):
    """
    Update the status of a ticket.

    TODO: Implement UPDATE operation.
    """

    # Error hadling to prevent crashes  
    try:
        # Get cursor
        cursor = conn.cursor()

        # Execute and commit
        cursor.execute(
            "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
            (new_status, ticket_id)
        )
        conn.commit()

        print(f"✅ Ticket '{ticket_id}' updated to status '{new_status}'")
  
        # Return cursor.rowcount
        return cursor.rowcount

    except Exception as e:
        print(f"❌ Failed to update ticket '{ticket_id}': {e}")
        return 0



def delete_ticket(conn, ticket_id):
    """
    Delete a ticket from the database.
    """
    try:
        # Get cursor
        cursor = conn.cursor()

        # Execute and commit
        cursor.execute(
            "DELETE FROM it_tickets WHERE ticket_id = ?",
            (ticket_id,)
        )
        conn.commit()

        # return row count
        return cursor.rowcount

    except Exception as e:
        print(f"❌ Error deleting ticket '{ticket_id}': {e}")
        return 0

def get_unresolved_tickets(conn):
    """
    Retrieve tickets with no resolved date.
    """
    query = """
    SELECT * FROM it_tickets
    WHERE resolved_date IS NULL OR resolved_date = ''
    ORDER BY priority DESC
    """

    df =  pd.read_sql_query(query, conn)
    return df

# 📊 Staff or process causing ticket delays
def get_ticket_delays(conn):
    """
    Identify staff members or process stages causing the most unresolved tickets.
    Shows counts of unresolved tickets by assigned staff and status.
    """
    # Count unresolved tickets by assigned staff
    staff_query = """
        SELECT assigned_to, COUNT(*) AS unresolved_count
        FROM it_tickets
        WHERE resolved_date IS NULL OR resolved_date = ''
        GROUP BY assigned_to
        ORDER BY unresolved_count DESC
    """
    staff_df = pd.read_sql_query(staff_query, conn)

    # Count unresolved tickets by current status (process stage)
    status_query = """
        SELECT status, COUNT(*) AS unresolved_count
        FROM it_tickets
        WHERE resolved_date IS NULL OR resolved_date = ''
        GROUP BY status
        ORDER BY unresolved_count DESC
    """
    status_df = pd.read_sql_query(status_query, conn)

    return staff_df, status_df
