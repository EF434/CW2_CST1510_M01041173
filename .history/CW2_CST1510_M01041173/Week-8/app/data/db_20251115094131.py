# Import necessary modules
import sqlite3
from pathlib import Path

# Define paths
DATA_DIR = Path("DATA")
DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database."""
    return sqlite3.connect(str(db_path))