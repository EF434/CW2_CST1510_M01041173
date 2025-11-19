# user_service.py includes functions originally from auth.py plus the migration function.

# --- IMPORTS ---
import bcrypt
import sqlite3
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user
from app.data.schema import create_users_table

import time # For challenge 3
import secrets

# --- PATHS & CONSTANTS ---
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

# Initialize dictionary
failed_attempts = {}
account_lock = {}

# Initialize required constants & file
MAX_ATTEMPTS = 3
ACCOUNT_LOCK_TIME = 300 # 5 minutes in seconds
SESSION_FILE = Path("sessions.txt")  # store session tokens (Challenge 4)
AVAILABLE_ROLES = ["user", "admin", "analyst"] # Define avalible roles



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

    cursor = conn.cursor()

    # Validate if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' already exists."

    # Hash the password
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode("utf-8")

    # --- Role validation (Challenge 2)
    if role is None or role.lower() not in AVALIBLE_ROLES:
        attempts = 3
        while attempts > 0:
            print(f"Available roles: {', '.join(AVALIBLE_ROLES)}")
            role_input = input(f"Enter role for '{username}': ").strip().lower()
            if role_input in AVALIBLE_ROLES:
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
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
        conn.close()
        return True, f"User '{username}' - {role} registered successfully as '{role}'!"
    
    # Error handling to prevent crashes
    except Exception as e:
        conn.close()
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
    # Open database connection
    conn = connect_database()
    cursor = conn.cursor()

    # Add user to tracking if not already present
    if username not in failed_attempts:
        failed_attempts[username] = 0

    # Check if account is locked
    if username in account_lock:
        current_time = time.time()
        remaining_time = int(account_lock[username] - current_time)
        if remaining_time > 0:
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            return False, f"🔒 '{username}' Account locked. Lock Time: {minutes}m {seconds}s"
        else:
            # Unlock account
            failed_attempts[username] = 0
            account_lock.pop(username)
    
    # Fetch user from database
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
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
    
    # Failed password attempt
    failed_attempts[username] += 1
    remaining_attempts = MAX_ATTEMPTS - failed_attempts[username] # calculate user's remainig attempts

    # Inform user of failed login and remaining attempts
    if remaining_attempts > 0:
        return False, f"❌ Incorrect password. Attempts used: {failed_attempts[username]}. Remaining: {remaining_attempts}"
    else:
        account_lock[username] = time.time() + ACCOUNT_LOCK_TIME
        return False, "🚫 Maximum failed attempts reached. Account locked for 5 minutes."
    

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


# === COMPLETE IMPLEMENTATION PROVIDED FOR migrate_users_from_file() ===
def migrate_users_from_file(conn, filepath= DATA_DIR / "users.txt"):
    """
    Migrate users from users.txt to the database.
    
    This is a COMPLETE IMPLEMENTATION as an example.
    
    Args:
        conn: Database connection
        filepath: Path to users.txt file
    """
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        print("   No users to migrate.")
        return
    
    cursor = conn.cursor()
    migrated_count = 0
    
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
                
                # Insert user (ignore if already exists)
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, 'user')
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except sqlite3.Error as e:
                    print(f"Error migrating user {username}: {e}")
    
    conn.commit()
    print(f"✅ Migrated {migrated_count} users from {filepath.name}")