import sys
from pathlib import Path

# Project root (my_app)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.data.db import connect_database, load_all_csv_data
from app.data.schema import create_all_tables
from app.services.user_service import migrate_users_from_file

DATA_DIR = PROJECT_ROOT / "DATA"

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
