# Import necessary modules
import sqlite3
from pathlib import Path
import pandas as pd


# Define paths
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

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
    try:
         return sqlite3.connect(str(db_path))
    except sqlite3.Error as e:
         print(f"❌ Could not connect to the database. Error: {e}")
         return None

# Function to load CSV data into a database table
def load_csv_to_table(conn, csv_path, table_name):
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
         # TODO: Check if CSV file exists
         if not Path(csv_path).exists():
            print(f"'{csv_path}' not found:")
            return 0

         # TODO: Read CSV using pandas.read_csv()
         df = pd.read_csv(csv_path)
    
         # TODO: Use df.to_sql() to insert data
         # Parameters: name=table_name, con=conn, if_exists='append', index=False
         df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    
         # TODO: Print success message and return row count
         row_count = len(df)
         print(f"✅Successfully loaded '{table_name}' from '{csv_path.name}'")
         return row_count
    
    except Exception as e:
        return None 

