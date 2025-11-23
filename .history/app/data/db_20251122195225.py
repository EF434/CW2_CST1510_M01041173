"""
db.py - Provides functions for database functions, e.g.:
    • Connecting to the SQLite database
    • Loading CSV data into database tables
"""

# -------------------------------
# Import required libraries
# -------------------------------
import sqlite3
from pathlib import Path
import pandas as pd

# -------------------------------
# Define paths
# -------------------------------
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

# ------------------------------------
# Connect & close the SQLite database
# ------------------------------------
def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    Create the database file if it doesn't exist.
    
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
         print(f"Error occurred! database not connected {e}")
         return None

# -----------------------------------
# Load CSV data into a database table
# -----------------------------------

from pathlib import Path
import pandas as pd

from pathlib import Path
import pandas as pd

def load_all_csv_data(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.
    Avoids duplicates by clearing table before loading.
    """
    try:
        csv_path = Path(csv_path)
        if not csv_path.exists():
            print(f"'{csv_path}' not found")
            return 0

        # Read CSV
        df = pd.read_csv(csv_path)

        # Drop 'id' column if exists
        if "id" in df.columns:
            df = df.drop(columns=["id"])

        # Strip whitespace from string columns to avoid mismatch
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Clear table first
        with conn:
            conn.execute(f"DELETE FROM {table_name}")

        # Insert into table
        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)

        row_count = len(df)
        print(f"✅ Successfully loaded '{table_name}' ({row_count} rows)")
        return row_count

    except Exception as e:
        print(f"⚠️ Error loading '{table_name}' from '{csv_path}': {e}")
        return 0
