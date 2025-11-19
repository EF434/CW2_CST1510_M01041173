# user_service.py includes functions originally from auth.py plus the migration function.

# --- IMPORTS ---
import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user
from app.data.schema import create_users_table

# Define paths
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

# --- COMPLETE IMPLEMENTATION PROVIDED FOR register_user() (Updated form Week 7 - Challenge 2)

# Define avalible roles
AVAILABLE_ROLES = ["user", "admin", "analyst"]

def register_user(username: str, password: str, role: str = None) -> tuple:
    """
    Register a new user in the database with hashed password and optional role.
    
    Args:
        username (str): User's login name
        password (str): Plaintext password (will be hashed)
        role (str, optional): Role for the user ('user', 'admin', 'analyst'). Defaults to 'user'.
        
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



# --- COMPLETE IMPLEMENTATION PROVIDED FOR login_user()
def login_user(username, password):
    """
    Authenticate a user against the database.
    
    This is a COMPLETE IMPLEMENTATION as an example.
    
    Args:
        username: User's login name
        password: Plain text password to verify
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    # Find user
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return False, "Username not found."
    
    # Verify password (user[2] is password_hash column)
    stored_hash = user[2]
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')
    
    if bcrypt.checkpw(password_bytes, hash_bytes):
        return True, f"Welcome, {username}!"
    else:
        return False, "Invalid password."


# --- COMPLETE IMPLEMENTATION PROVIDED FOR migrate_users_from_file()
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