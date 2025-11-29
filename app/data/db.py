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

def load_all_csv_data(conn, csv_path, table_name):
    """
    Load a CSV into a table only if empty.
    Drops 'id' for autoincrement and commits changes.
    """
    try:
        csv_path = Path(csv_path)
        if not csv_path.exists():
            print(f"'{csv_path}' not found")
            return 0

        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Table '{table_name}' already has data ({count} rows). Skipping CSV load.")
            return 0

        df = pd.read_csv(csv_path)

        if "id" in df.columns:
            df = df.drop(columns=["id"])

        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
        conn.commit()  # important!

        # Reset AUTOINCREMENT only if table was empty
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
        conn.commit()

        print(f"✅ Successfully loaded '{table_name}' ({len(df)} rows)")
        return len(df)

    except Exception as e:
        print(f"⚠️ Error loading '{table_name}' from '{csv_path}': {e}")
        return 0

# -------------------------------
# Save a chat message
# -------------------------------
def save_message(conn, username, domain, role, content):
    """
    Save a chat message directly using username.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history (user_id, domain, role, content)
            VALUES (?, ?, ?, ?)
        """, (username, domain, role, content))
        conn.commit()
    except sqlite3.Error as e:
        print(f"⚠️ Error saving message: {e}")

# -------------------------------
# Load chat messages
# -------------------------------
def load_messages(conn, username, domain):
    """
    Load chat messages for a given username and domain.
    Returns list of dicts [{"role": ..., "content": ...}, ...]
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content FROM chat_history
            WHERE user_id = ? AND domain = ?
            ORDER BY id ASC
        """, (username, domain))
        rows = cursor.fetchall()
        return [{"role": r[0], "content": r[1]} for r in rows]
    except sqlite3.Error as e:
        print(f"⚠️ Error loading messages: {e}")
        return []