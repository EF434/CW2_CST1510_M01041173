"""
db.py - Provides functions for database management, including:
    • Connecting to the SQLite database
    • Loading CSV data into database tables
"""

# -------------------------------
# Import necessary libraries
# -------------------------------
import sqlite3
from pathlib import Path
import pandas as pd

# -------------------------------
# Define paths
# -------------------------------
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

# -------------------------------
# Connect to the SQLite database
# -------------------------------
def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    Creates the database file if it doesn't exist.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        sqlite3.Connection: Database connection object
    """
    # Handle database connection errors using try-except
    try:
         return sqlite3.connect(str(db_path))
    
    # Handle SQLite errors during database connection
    except sqlite3.Error as e:
         print(f"Error occured! database not connected {e}")
         return None

# -----------------------------------
# Load CSV data into a database table
# -----------------------------------

def load_all_csv_data(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.
    
    TODO: Implement this function.
    
    Args:
        conn: Database connection
        csv_path: Path to CSV file
        table_name: Name of the target table
        
    Returns:
        int: Number of rows loaded
    """
    try:
         # Check if CSV file exists
         csv_path = Path(csv_path)
         if not csv_path.exists():
            print(f"'{csv_path}' not found:")
            return 0

         # Read CSV using pandas.read_csv()
         df = pd.read_csv(csv_path)
    
         # Use df.to_sql() to insert data
         # Parameters: name=table_name, con=conn, if_exists='append', index=False
         df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    
         # Print success message and return row count
         row_count = len(df)
         print(f"✅Successfully loaded '{table_name}' from '{csv_path.name}'")
         return row_count
    
    except Exception as e:
        print(f"⚠️ Error loading '{table_name}' from '{csv_path}': {e}")
        return 0 
# --------- ## ---------- #

