# Import necessary modules
import sqlite3
from pathlib import Path

# Define paths
DATA_DIR = Path("DATA")
DB_PATH = Path("DATA") / "intelligence_platform.db"

# Create DATA folder if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Function to connect to the SQLite database
def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    Creates the database file if it doesn't exist.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        sqlite3.Connection: Database connection object
    """
    return sqlite3.connect(str(db_path))