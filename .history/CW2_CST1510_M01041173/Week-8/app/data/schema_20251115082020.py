# schema.py
"""
Module to define database schema and create tables.
"""

# COMPLETE IMPLEMENTATION PROVIDED FOR create_users_table()
def create_users_table(conn):
    """
    Create the users table if it doesn't exist.
    
    This is a COMPLETE IMPLEMENTATION as an example.
    Study this carefully before implementing the other tables!
    
    Args:
        conn: Database connection object
    """
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
    
    # Execute the SQL statement
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Users table created successfully!")
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
    # TODO: Get a cursor from the connection
    cursor = conn.cursor()
    
    # TODO: Write CREATE TABLE IF NOT EXISTS SQL statement
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
    # Follow the pattern from create_users_table()
    
    # TODO: Execute the SQL statement
    cursor.execute(create_table_sql)
    
    # TODO: Commit the changes
    conn.commit()
    
    # TODO: Print success message
    print("🛡️ 'cyber_incidents' table created successfully!")
    


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
    cursor = conn.cursor()
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
    cursor.execute(create_table_sql)
    conn.commit()
    print("📊 'datasets_metadata' table created successfully!")
    


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
    cursor = conn.cursor()
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
    cursor.execute(create_table_sql)
    conn.commit()
    print("🎫  'it_tickets' table created successfully!")