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

