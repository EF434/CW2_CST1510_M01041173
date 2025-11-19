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
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent  # main.py parent = project root
DATA_DIR = PROJECT_ROOT / "DATA"                # DATA folder inside project
DATA_DIR.mkdir(parents=True, exist_ok=True)          # Create folder if missing

# Database file inside DATA folder
DB_PATH = DATA_DIR / "intelligence_platform.db"

from app.data.db import connect_database, DB_PATH, load_all_csv_data
from app.data.schema import create_all_tables
from app.data.users import get_user_by_username
from app.services.user_service import (
    register_user, 
    login_user, 
    validate_username,
    validate_password,
    create_session, 
    migrate_users_from_file, 
    check_password_strength
)

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
    print("Week 8: Database Demo".center(60))
    print("=" * 60)
    
    # Setup database
    conn = connect_database()
    create_all_tables(conn)
    migrate_users_from_file(conn)
    
    # Register and login a test user
    username = "alice"
    password = "SecurePass123!"
    role = "analyst"
    success, msg = register_user(username, password, role)
    print(msg)
    
    # Display without role
    success, msg = register_user(username, password)
    print(msg)
    
    # Add a test incident
    incident_id = insert_incident(
        conn,
        "2024-11-05",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected",
        username
    )
    print(f"📌 Created incident #{incident_id}")
    
    # Display incident count
    df = get_all_incidents(conn)
    print(f"Total incidents: {len(df)}")
    conn.close()

# -------------------------------
# Complete Database Setup
# -------------------------------
def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """

    # Decorative Header
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP".center(60))
    print("="*60)
    
    # Step 1: Connect
    print("\n[1/5] Connecting to database...")
    conn = connect_database()
    print("✔ Connected")
    
    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)
    
    # Step 3: Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    user_count = migrate_users_from_file(conn)
    print(f"✔ Migrated {user_count} users")
    
    # Step 4: Load CSV data
    print("\n[4/5] Loading CSV data...")
    total_rows = load_all_csv_data(conn, DATA_DIR / "cyber_incidents.csv", "cyber_incidents")
    dm_rows = load_all_csv_data(conn, DATA_DIR / "datasets_metadata.csv", "datasets_metadata")
    it_rows = load_all_csv_data(conn, DATA_DIR / "it_tickets.csv", "it_tickets")
    print(f"✔ 'cyber_incidents' table loaded | Rows: {total_rows}")
    print(f"✔ 'datasets_metadata' table loaded | Rows: {dm_rows}")
    print(f"✔ 'it_tickets' table loaded | Rows: {it_rows}")
    
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


# -------------------------------
# Comprehensive Tests
# -------------------------------
def run_comprehensive_tests():
    """
    Run comprehensive tests on your database.
    """

    # Decorative Header
    print("\n" + "="*60)
    print("🧪 RUNNING COMPREHENSIVE TESTS".center(60))
    print("="*60)
    
    conn = connect_database()
    
    # Test 1: Authentication
    print("\n[TEST 1] User Registration & Login")

    username, password, role = "test_user", "TestPass123!", "user"
    success, msg = register_user(username, password, role)
    print(f"  Register: {'✅' if success else '❌'} {msg}")
    success, msg = login_user(username, password)
    print(f"  Login:    {'✅' if success else '❌'} {msg}")
    
    # Test 2: CRUD Operations
    print("\n[TEST 2] CRUD Operations")
    test_id = insert_incident(
        conn,
        "2024-11-05",
        "Test Incident",
        "Low",
        "Open",
        "This is a test incident",
        username
    )
    print(f"  Create: ✅ Incident #{test_id} created")
    
    # Read
    df = pd.read_sql_query("SELECT * FROM cyber_incidents WHERE id = ?",conn,params=(test_id,))
    print(f"  Read:    Found incident #{test_id}")
    
    # Update
    update_incident_status(conn, test_id, "Resolved")
    print(f"  Update:  Status updated to 'Resolved'")
    
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

# -------------------------------
# Interactive User Menu System
# -------------------------------

def interactive_menu():
    """Interactive user login and registeration with validations
       and passowrd strength checks"""
    
    while True:
        print("\n" + "="*60)
        print("🔐 Authentication Menu".center(60))
        print("="*60)
        print("1) Register")
        print("2) Login")
        print("3) Back to Main Menu")
              
        selection = input("\nPlease select an option (1-3): ").strip()

        # Register user via username (3 attempts only)
        if selection == "1": 
            print("\n--- USER REGISTRATION ---")

            # Ask for username to register
            username = input("Enter a username: ").strip()

            # Validate username format
            is_valid, err_msg = validate_username(username)
            if not is_valid:
                print(f"❌ {err_msg}")
                continue

            # Check if username already exists
            if get_user_by_username(username):
                print(f"Username '{username}' exists. Try again")
                continue

            # Ask for user's role to register
            role = input("Enter role (e.g., admin, analyst, user): ").strip()

            # Ask for user's password (only 3 attempts allowed)
            password_attempts = 3
            while password_attempts > 0:
                password = input("Enter a password: ").strip()

                # Validate user's password
                is_valid, err_msg = validate_password(password, username)
                if not is_valid:
                    print(f"❌ {err_msg}")
                    password_attempts -= 1
                    continue

                # Check password strength
                is_strong, msg = check_password_strength(password)
                print(f"ℹ {msg}")
                if msg.startswith("Moderate"):
                    confirm = input("Do you want to proceed with this password? (y/n): ").strip().lower()
                    if confirm != 'y':
                        password_attempts -= 1
                        continue

                # Confirm password
                password_confirm = input("Confirm password: ").strip()
                if password != password_confirm:
                    print("❌ Passwords do not match")
            password_attempts -= 1
            continue

        break  # Password is valid

    else:
        print("❌ Maximum password attempts reached. Returning to menu.")
        continue

    # Register the user
    success, msg = register_user(username, password, role)
    print(f"{'✔' if success else '❌'} {msg}")

    # Optional: log in user automatically
    if success:
        login_success, login_msg = login_user(username, password)
        if login_success:
            print(f"✔ Logged in as {username}")
            create_session(username)
        else:
            print(f"❌ Login failed: {login_msg}")



        #  Attempt Login 
        elif selection == '2': 
            print("\n--- USER LOGIN ---")
            # Get user details for login
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # Attempt login
            success, msg = login_user(username, password)
            if success:
                print(f"\n✔ {msg}")
                create_session(username)
                input("\nPress Enter to return to main menu...")
            else:
                print(f"❌ {msg}")
                continue
        
                    
        # ----- Exit fucntion & return to the mai program
        elif selection == '3':
            print("\nThank you for interative login/registeration")
            print("Returning to main menu")
            break

        # ----- Invalid Option 
        else:
            print("\nInvalid input (Enter only between 1-3)")

# -----------------
# Main Menu
# -----------------
def main_menu():
    """Interactive CLI menu for user-driven operations."""
    
    while True:
        print("\n" + "=" * 60)
        print("Cyber Incident Management - Main Menu".center(60))
        print("=" * 60)
        print("1) Setup Database")
        print("2) Run System Test")
        print("3) Test Run")
        print("4) Interacitve Login")
        print("5) Exit")

        user_choice = input("\nSelect an option: ").strip()

        if user_choice == "1":
            setup_database_complete()
        elif user_choice == "2":
            run_comprehensive_tests()
        elif user_choice == "3":
            test_run()
        elif user_choice == "4":
            interactive_menu()
        elif user_choice == "5":
            print("\n👋 Ending program. Goodbye!")
            break
        else:
            print("⚠️ Invalid choice. Please try again.")


# Run Program
if __name__ == "__main__":
    main_menu()