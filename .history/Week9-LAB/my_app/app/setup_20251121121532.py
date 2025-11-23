import sys
from pathlib import Path

# Add the actual folder where db.py exists to sys.path
DB_FOLDER = Path(r"C:\CST1510\CW2_CST1510_M01041173\app")
if str(DB_FOLDER) not in sys.path:
    sys.path.insert(0, str(DB_FOLDER))

from data.db import connect_database, load_all_csv_data
from data.schema import create_all_tables
from services.user_service import migrate_users_from_file

DATA_DIR = Path(r"C:\CST1510\CW2_CST1510_M01041173\DATA")


def initialize_system():
    """Create tables and import all CSVs/users into the DB."""
    conn = connect_database()
    
    # 1. Create all tables
    create_all_tables(conn)

    # 2. Migrate users from text file
    migrate_users_from_file()

    # 3. Load CSVs into their tables
    load_all_csv_data(conn, DATA_DIR / "cyber_incidents.csv", "cyber_incidents")
    load_all_csv_data(conn, DATA_DIR / "datasets_metadata.csv", "datasets_metadata")
    load_all_csv_data(conn, DATA_DIR / "it_tickets.csv", "it_tickets")

    conn.close()
    return "✔ Database initialized and CSVs imported!"
