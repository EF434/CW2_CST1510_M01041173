"""
schema.py - Define functions to create database tables
Tables included:
  • users
  • cyber_incidents
  • datasets_metadata
  • it_tickets
"""

# -----------------
# Import modules
# -----------------
import sqlite3 # required for error handling
from app.data.db import c

# -------------------------------------------------------
# create_users_table() function to create 'users' table
# -------------------------------------------------------

def create_users_table(conn):
    """
    Create the users table if it doesn't exist.

    Args:
        conn: Database connection object
    """

    # Get a cursor 
    cursor = conn.cursor()
    
    # SQL statement to create users table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    # Use try-except block to handle potential SQLite errors
    try: 
        # Executing the SQL statement
        cursor.execute(create_table_sql)

        # Commit the changes
        conn.commit()

        # Display message
        print("𝄜 Users table created successfully!")

    except sqlite3.Error as e:
        print(f"❌ Error: Users table not created: {e}")


# --------------------------------------------------------------------
# create_cyber_incidents_table() function to create cyber_incidents table
# --------------------------------------------------------------------

def create_cyber_incidents_table(conn):
    """
    Create the cyber_incidents table.
    
    TODO: Implement this function following the users table example above.
    
    Required columns:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - date: TEXT (format: YYYY-MM-DD)
    - incident_type: TEXT (e.g., 'Phishing', 'Malware', 'DDoS')
    - severity: TEXT (e.g., 'Critical', 'High', 'Medium', 'Low')
    - status: TEXT (e.g., 'Open', 'Investigating', 'Resolved', 'Closed')
    - description: TEXT
    - reported_by: TEXT (username of reporter)
    - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """
    # Get a cursor from the connection
    cursor = conn.cursor()
    
    # SQL statement to create 'cyber_incidents' table
    # Write CREATE TABLE IF NOT EXISTS SQL statement
    create_table_sql = """
             CREATE TABLE IF NOT EXISTS cyber_incidents (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             date TEXT,
             incident_type TEXT,
             severity TEXT,
             status TEXT,
             description TEXT,
             reported_by TEXT,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Handle exceptions during table creation
    try: 
        # Execute the SQL statement
        # Use 'with' to auto-commit and handle errors safely
        with conn:
            cursor.execute(create_table_sql)
            # Display message
            print("𝄜 'cyber_incidents' table created successfully!")
    
    # Commit the changes
    # Using 'with conn:' automatically commits changes

    except sqlite3.Error as e:
        print(f"❌ Error creating cyber_incidents table: {e}")
    
   
# ------------------------------------------------------------------------
# create_datasets_metadata_table() function to create datasets_metadata table
# -----------------------------------------------------------------------

def create_datasets_metadata_table(conn):
    """
    Create the datasets_metadata table.
    
    TODO: Implement this function following the users table example.
    
    Required columns:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - dataset_name: TEXT NOT NULL
    - category: TEXT (e.g., 'Threat Intelligence', 'Network Logs')
    - source: TEXT (origin of the dataset)
    - last_updated: TEXT (format: YYYY-MM-DD)
    - record_count: INTEGER
    - file_size_mb: REAL
    - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """
    # TODO: Implement following the users table pattern
 
    # Get a cursor from the connection
    cursor = conn.cursor()

    # SQL statement to create 'datasets_metadata' table
    create_table_sql = """
             CREATE TABLE IF NOT EXISTS datasets_metadata (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             dataset_name TEXT NOT NULL,
             category TEXT,
             source TEXT,
             last_updated TEXT,
             record_count INTEGER,
             file_size_mb REAL,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   
    )
    """
    # try-except for error handling
    try:
        # Execute the SQL statement
        # Use 'with' to auto-commit and handle errors safely
        with conn:
            cursor.execute(create_table_sql)
            print("𝄜 'datasets_metadata' table created successfully!")
    except sqlite3.Error as e:
         print(f"❌ Error creating datasets_metadata table: {e}")
    

# --------------------------------------------------------------------
# create_it_tickets_table() function to create it_tickets table
# --------------------------------------------------------------------

def create_it_tickets_table(conn):
    """
    Create the it_tickets table.
    
    TODO: Implement this function following the users table example.
    
    Required columns:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - ticket_id: TEXT UNIQUE NOT NULL
    - priority: TEXT (e.g., 'Critical', 'High', 'Medium', 'Low')
    - status: TEXT (e.g., 'Open', 'In Progress', 'Resolved', 'Closed')
    - category: TEXT (e.g., 'Hardware', 'Software', 'Network')
    - subject: TEXT NOT NULL
    - description: TEXT
    - created_date: TEXT (format: YYYY-MM-DD)
    - resolved_date: TEXT
    - assigned_to: TEXT
    - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """
    # Get a cursor from the connection
    cursor = conn.cursor()

    # SQL statement to create 'it_tickets' table
    create_table_sql = """
                CREATE TABLE IF NOT EXISTS it_tickets (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                priority TEXT,
                status TEXT,
                category TEXT,
                subject TEXT NOT NULL,
                description TEXT,
                created_date TEXT,
                resolved_date TEXT,
                assigned_to TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """                   
    try:
        with conn:
            cursor.execute(create_table_sql)
        print("𝄜 'it_tickets' table created successfully!")
    except sqlite3.Error as e:
         print(f"❌ Error creating it_tickets table: {e}")

# ------------------------------------
# Function to create all tables 
# ------------------------------------

def create_all_tables(conn):
    """
    Create all four tables in the database.

    Args:
        conn: Database connection object
    """
    # Call functions of every table
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)

# --- End of schema.py ---
