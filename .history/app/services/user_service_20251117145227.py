# user_service.py includes functions originally from auth.py plus the migration function.

# --- IMPORTS ---
import bcrypt
import sqlite3
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user

import time # For challenge 3
import secrets # For challenge 4

# --- PATHS & CONSTANTS ---
# user_service.py is in app/services/
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # go up 2 levels to reach project root
DATA_DIR = PROJECT_ROOT / "DATA"
USERS_FILE = DATA_DIR / "users.txt"

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
        
        # Failed password attempt
        failed_attempts[username] += 1
        remaining_attempts = MAX_ATTEMPTS - failed_attempts[username] # calculate user's remainig attempts

        # Inform user of failed login and remaining attempts
        if remaining_attempts > 0:
            return False, f"❌ Incorrect password. Attempts used: {failed_attempts[username]}. Remaining: {remaining_attempts}"
        else:
            account_lock[username] = time.time() + ACCOUNT_LOCK_TIME
            return False, "🚫 Maximum failed attempts reached. Account locked for 5 minutes."
    finally:
        conn.close()

# --------- Step10. Implement Input Validation
def validate_username(username: str) -> tuple:
    '''
    Validates username format.
    Args:
    username (str): The username to validate

    Returns:
    tuple: (bool, str) - (is_valid, error_message)
    '''
    # Check for empty username
    if not username:
        return False, "Username cannot be empty."
    
    # Check username length
    if len(username) < 4 or len(username) > 20:
        return False, "Username must be between 4 and 20 characters long."
    
    # Check username pattern by regex (alphanumeric and underscores only)
    if not re.match("^[A-Za-z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."
    
    # Check for underscores at start or end
    if username.startswith('_') or username.endswith('_'):
        return False, "Username cannot start or end with an underscore."
    
    # Check if username is entirely numeric
    if username.isdigit() or username.isnumeric():
        return False, "Username cannot be entirely numeric."
    
    # Check for spaces in username
    if username.isspace() or ' ' in username:
        return False, "Username cannot contain spaces."
    
    return True, "Username is valid."


def validate_password(password: str, username: str) -> tuple:
    '''
    Validates password strength.

    Args:
    password (str): The password to validate

    Returns:
    tuple: (bool, str) - (is_valid, error_message)

    '''
    # Check for empty password
    if not password:   
        return False, "Password cannot be empty."
    
    # Check password length
    if len(password) < 6 or len(password) > 50:
        return False, "Password must be between 6 and 50 characters long."

    # Check letters and digits with regex
    if not (re.search(r"[a-z]", password) and re.search(r"[A-Z]", password) and re.search(r"\d", password)):
        return False, "Password must contain at least one uppercase letter, one lowercase letter, and one digit."
    if password.isspace() or ' ' in password:
        return False, "Password cannot contain spaces."
    if username.lower() in password.lower():
        return False, "Password cannot contain your username."
    
    return True, "Password is valid." 

        
# Challenge 1: Password Strength Indicator
def check_password_strength(password):
    '''
   Evaluates password strength.

   Returns:
   str: "Weak", "Medium", or "Strong"
    '''
    # Define weak passwords list
    WEAK_PASSWORDS = ["password", "admin", "welcome", "login", "letmein",
    "iloveyou", "monkey", "dragon", "sunshine", "princess",
    "freedom", "whatever", "trustno1", "hello", "pass",
    "qwerty", "abc123", "123456", "12345678", "12345"]

    # Check against weak passwords
    if password.lower() in WEAK_PASSWORDS:
        return False, f"Weak password ❌: '{password}' commonly used password."
    
    # Check for substrings of weak passwords
    for pwd in WEAK_PASSWORDS:
        if pwd in password.lower():
            return False, f"Weak password ❌: contains commonly used password '{pwd}'."
    
    # Initialize criteria flags
    upper = lower = digit = special_char = False
    symbols = string.punctuation
    
    # Check length
    if len(password) < 8:
        return False, "Password too short. Minimum 8 characters."
  
    if len(password) > 50:
        return False, "Password too long. Maximum 50 characters allowed."
    
    # Evaluate character types
    for char in password:
        if char.isupper():
            upper = True
        elif char.islower():
            lower = True
        elif char.isdigit():
            digit = True
        elif char in symbols:
            special_char = True
        elif char.isspace():
            return False, "Spaces are not allowed in the password."
        
    # Calculate strength points
    strength_points = upper + lower + digit + special_char
    bar = "█" * strength_points + "░" * (4 - strength_points)

    # Display password strength bar
    print("\n" + "-" * 55)
    print(f" Password Strength Indicator: [{bar}]")
    print("-" * 55)

    # Determine strength level
    if strength_points < 3:
        return False, "Weak password ❌: must include uppercase, lowercase, digit, and special character."
    elif strength_points == 3:
        return True, "Moderate password ⚠️: consider adding the missing character type for extra strength."
    else:
        return True, "Strong password ✅: good job!"
    
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