"""
# main.py - Interactive CLI for Cyber Incident Management
-------------------------------------------------------
Features:
1. Complete database setup
2. User migration from file
3. Registration & login
4. Incident CRUD operations
5. Analytical queries
6. Demo & comprehensive tests
"""

# ---------------
# Imports
# ---------------
import sys
from pathlib import Path
import pandas as pd

# Add current folder to sys.path for local imports
sys.path.append(str(Path(__file__).resolve().parents[0]))  # Adjust as needed


from app.data.db import connect_database, DB_PATH, load_all_csv_data
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import (
      insert_incident,
      get_all_incidents, 
      update_incident_status, 
      delete_incident, 
      get_incidents_by_type_count,
      get_high_severity_by_status
)

# ---------------
# test Function
# ---------------

def test_run():
    """Run a simple demo showcasing database setup, user registration, login, and incident creation."""

    # Decorative Header
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)
    
    # Setup database
    conn = connect_database()
    create_all_tables(conn)
    
    # 2. Migrate users
    migrate_users_from_file(conn)
    
    # 3. Test authentication
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(msg)
    
    success, msg = login_user("alice", "SecurePass123!")
    print(msg)
    
    # 4.  # Add a test incident
    incident_id = insert_incident(
        conn,
        "2024-11-05",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected",
        "alice"
    )
    print(f"📌 Created incident #{incident_id}")
    
    # 5. Query data - Display count
    df = get_all_incidents(conn)
    print(f"Total incidents: {len(df)}")

def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)
    
    # Step 1: Connect
    print("\n[1/5] Connecting to database...")
    conn = connect_database()
    print("Connected")
    
    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)
    
    # Step 3: Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    user_count = migrate_users_from_file(conn)
    print(f"✔ Migrated {user_count} users")
    
    # Step 4: Load CSV data
    print("\n[4/5] Loading CSV data...")
    total_rows = load_all_csv_data(conn, "DATA/cyber_incidents.csv", "cyber_incidents")
    
    # Step 5: Verify
    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()
    
    # Count rows in each table
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")
    
    conn.close()
    
    print("\n" + "="*60)
    print(" DATABASE SETUP COMPLETE!")
    print("="*60)
    print(f"\n Database location: {DB_PATH.resolve()}")
    print("\nYou're ready for Week 9 (Streamlit web interface)!")


def run_comprehensive_tests():
    """
    Run comprehensive tests on your database.
    """
    print("\n" + "="*60)
    print("🧪 RUNNING COMPREHENSIVE TESTS")
    print("="*60)
    
    conn = connect_database()
    
    # Test 1: Authentication
    print("\n[TEST 1] Authentication")
    success, msg = register_user("test_user", "TestPass123!", "user")
    print(f"  Register: {'✅' if success else '❌'} {msg}")
    
    success, msg = login_user("test_user", "TestPass123!")
    print(f"  Login:    {'✅' if success else '❌'} {msg}")
    
    # Test 2: CRUD Operations
    print("\n[TEST 2] CRUD Operations")
    
    # CRUD Test
    test_id = insert_incident(
        conn,
        "2024-11-05",
        "Test Incident",
        "Low",
        "Open",
        "This is a test incident",
        "test_user"
    )
    print(f"  Create: ✅ Incident #{test_id} created")
    
    # Read
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE id = ?",
        conn,
        params=(test_id,)
    )
    print(f"  Read:    Found incident #{test_id}")
    
    # Update
    update_incident_status(conn, test_id, "Resolved")
    print(f"  Update:  Status updated")
    
    # Delete
    delete_incident(conn, test_id)
    print(f"  Delete:  Incident deleted")
    
    # Test 3: Analytical Queries
    print("\n[TEST 3] Analytical Queries")
    
    df_by_type = get_incidents_by_type_count(conn)
    print(f"  By Type:     Found {len(df_by_type)} incident types")
    
    df_high = get_high_severity_by_status(conn)
    print(f"  High Severity: Found {len(df_high)} status categories")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)


# --- CLI Menu ---------------------------------------------------------------

def main_menu():
    """Simple user menu for running system features."""
    
    while True:
        print("\n" + "=" * 60)
        print("Cyber Incident Management - Main Menu".center(60))
        print("=" * 60)
        print("1) Setup Database")
        print("2) Run Full Test Suite")
        print("3) Run Demo")
        print("4) Exit")

        user_choice = input("\nSelect an option: ").strip()

        if user_choice == "1":
            setup_database_complete()
        elif user_choice == "2":
            run_comprehensive_tests()
        elif user_choice == "3":
            test_run()
        elif user_choice == "4":
            print("\n👋 Exiting program. Goodbye!")
            break
        else:
            print("⚠️ Invalid choice. Please try again.")


# --- Program Entry Point ----------------------------------------------------

if __name__ == "__main__":
    main_menu()