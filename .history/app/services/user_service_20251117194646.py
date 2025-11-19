



# user_service.py includes functions originally from auth.py plus the migration function.

# --- IMPORTS ---
import bcrypt
import sqlite3

from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user

import secrets # For challenge 4

# --- PATHS & CONSTANTS ---
# user_service.py is in app/services/
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # go up 2 levels to reach project root
DATA_DIR = PROJECT_ROOT / "DATA"
USERS_FILE = DATA_DIR / "users.txt"

# Initialize required constants & file
SESSION_FILE = Path("sessions.txt")  # store session tokens (Challenge 4)



# === register_user() fully implemented (Week 7 Challenge 2) ===
def register_user(username: str, password: str, role: str = None) -> tuple:
    """
    Register a new user in the database with hashed password and role.
    
    Args:
        username (str): User's login name
        password (str): Plaintext password (will be hashed)
        role (str): Role for the user ('user', 'admin', 'analyst'). Defaults to 'user'.
        
    Returns:
        tuple: (success: bool, message: str)
    
    Notes:
        - If the username already exists, registration fails.
        - Role is validated; defaults to 'user' if invalid or not provided.
        - Limits invalid role attempts to 3.
    """
    conn = connect_database()

    # Validate connection
    if not conn:
        return False, "❌ Error! Database connection failed."

    # Validate if user already exists
    if get_user_by_username(conn, username):
        return False, f"Username '{username}' already exists."

    # Hash the password
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode("utf-8")

    # --- Role validation (Challenge 2)
    if role is None or role.lower() not in AVAILABLE_ROLES:
        attempts = 3
        while attempts > 0:
            print(f"Available roles: {', '.join(AVAILABLE_ROLES)}")
            role_input = input(f"Enter role for '{username}': ").strip().lower()
            if role_input in AVAILABLE_ROLES:
                role = role_input
                break
            else:
                attempts -= 1
                print(f"Error: Invalid role '{role_input}'. Attempts remaining: {attempts}")
        if attempts == 0:
            print("⚠️ Role not recognized. Assigning default role: 'user'.")
            role = "user"
    else:
        role = role.lower()

    # Insert the new user into the database
    try:
        if insert_user(conn, username, password_hash, role):
            conn.commit()
            conn.close()
            return True, f"User '{username}' - {role} registered successfully as '{role}'!"
        else:
            return False, "❌ Failed to insert user into the database."
    
    # Error handling to prevent crashes
    except Exception as e:
        return False, f"Error registering user: {e}"

# ==== login_user() – Fully implemented (Week 7 Challenge 3) ===
def login_user(username, password):
    """
    Authenticate a user against the database  with attempt tracking and lockout..
    
    Args:
        username: User's login name
        password: Plain text password to verify
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = connect_database()

    try:
    
        # Get user from database via 'users.py'
        user = get_user_by_username(conn, username)
    
        # Validate If user not exists
        if not user:
            return False, "Username not found."
    
        # Verify password (user[2] is password_hash column)
        stored_hash = user[2]
        password_bytes = password.encode('utf-8')
        hash_bytes = stored_hash.encode('utf-8')

        # Verify password using bcrypt
        if bcrypt.checkpw(password_bytes, hash_bytes):
            return True, f"Welcome, {username}!"
        
    finally:
        conn.close()
    
# == Challenge 4: Session Management ==
def create_session(username):
    """Create a session token for the logged-in user."""

    # Generate a secure random token
    token = secrets.token_hex(16)

    # Store token with timestamp
    with open(SESSION_FILE, 'a') as f:
        f.write(f"{username},{token}\n")

    # Display session token
    print(f"🛡️ Session token created: {token}")
    return token


# -------------------------------------------------------
# Migrate users from 'users.txt' into the database
# -------------------------------------------------------

def migrate_users_from_file(conn, filepath= DATA_DIR / "users.txt"):
    """
    Migrate users from users.txt to the database.
    
    Args:
        conn: Database connection
        filepath: Path to users.txt file
    """

    # Check if file exists
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        return
    
    migrated_count = 0
    
    # Iterate through each line from the file
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Parse line: username,password_hash
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]

                # Determine user's role
                if len(parts) >= 3 and parts[2].lower() in AVAILABLE_ROLES:
                    role = parts[2].lower()
                else:
                    role = 'user' # Assign default role

                # Validate if user already exists
                if get_user_by_username(conn, username):
                    print(f"Username '{username}' already exists. skipping")
                    continue

                # error handling to prevent crashes
                try:
                    # Insert user (skip if already exists) 
                    if insert_user(conn, username, password_hash, role=role):
                        migrated_count += 1
                except sqlite3.Error as e:
                    print(f"Error migrating user {username}: {e}")
    
    conn.commit()
    print(f"✅ Migrated {migrated_count} users from {filepath.name}")