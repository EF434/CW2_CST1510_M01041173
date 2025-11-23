'''
Name: Emaan Fatima
MISI: M01041173
Course: CST1510 - Programming for Data Communication and Networks
CST1510 Week 7 Lab: Secure Authentication System
'''

# --------- Step 3 - Import Required Modules
import bcrypt
import os
from pathlib import Path
import string
import re
import time
import secrets

# --------- Step 6. Define Constants & Files
DATA_DIR = Path("DATA")
DATA_DIR.mkdir(exist_ok=True)
USER_DATA_FILE = DATA_DIR / "users.txt"
SESSION_FILE = DATA_DIR / "sessions.txt"
MAX_ATTEMPTS = 3
ACCOUNT_LOCK_TIME = 300  # seconds

# Dictionary to track failed attempts
failed_attempts = {}

# --------- Step 4 - Password Hashing
def hash_password(plain_text_password: str) -> str:
    password_bytes = plain_text_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

# --------- Step 5 - Password Verification
def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Error during password verification: {e}")
        return False

# --------- Step 8 - Check if User Exists
def user_exists(username: str) -> bool:
    if not USER_DATA_FILE.exists():
        return False
    try:
        with open(USER_DATA_FILE, "r") as f:
            for line in f:
                saved_username = line.strip().split(",")[0]
                if username.lower() == saved_username.lower():
                    return True
    except Exception as e:
        print(f"Error checking user existence: {e}")
    return False

# --------- Step 7 - Register User
def register_user(username: str, password: str) -> tuple[bool, str]:
    if not username.strip() or not password.strip():
        return False, "Username and password cannot be empty."
    if user_exists(username):
        return False, f"Error: Username '{username}' already exists."
    hashed_password = hash_password(password)
    try:
        with open(USER_DATA_FILE, "a") as f:
            f.write(f"{username},{hashed_password}\n")
        return True, f"User '{username}' registered successfully!"
    except Exception as e:
        return False, f"Error during registration: {e}"

# --------- Step 9 - Login User
def login_user(username: str, password: str) -> tuple[bool, str]:
    if not USER_DATA_FILE.exists():
        return False, "⚠️ No users registered yet."

    if username not in failed_attempts:
        failed_attempts[username] = 0

    if failed_attempts[username] >= MAX_ATTEMPTS:
        return False, f"🚫 Account is locked. Try again in {ACCOUNT_LOCK_TIME // 60} minutes."

    try:
        with open(USER_DATA_FILE) as f:
            username_found = False
            for line in f:
                parts = line.strip().split(",", 1)
                if len(parts) < 2:
                    continue
                user, hash_pw = parts
                if user == username:
                    username_found = True
                    if verify_password(password, hash_pw):
                        failed_attempts[username] = 0
                        return True, "✅ Login successful!"
                    else:
                        failed_attempts[username] += 1
                        remaining = MAX_ATTEMPTS - failed_attempts[username]
                        if remaining > 0:
                            return False, f"❌ Incorrect password. Attempts remaining: {remaining}"
                        else:
                            add_failed_attempt(username)
                            return False, "🚫 Account locked due to too many failed attempts."
        if not username_found:
            return False, "❌ Username not found."
    except Exception as e:
        return False, f"Error during login: {e}"

# --------- Step 10 - Username & Password Validation
def validate_username(username: str) -> tuple[bool, str]:
    if not username or len(username) < 4 or len(username) > 20:
        return False, "Username must be 4-20 characters long."
    if not re.match("^[A-Za-z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."
    if username.startswith("_") or username.endswith("_"):
        return False, "Username cannot start or end with an underscore."
    if username.isdigit():
        return False, "Username cannot be entirely numeric."
    if " " in username:
        return False, "Username cannot contain spaces."
    return True, "Username is valid."

def validate_password(password: str, username: str) -> tuple[bool, str]:
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 6 or len(password) > 50:
        return False, "Password must be 6-50 characters long."
    if not (re.search(r"[a-z]", password) and re.search(r"[A-Z]", password) and re.search(r"\d", password)):
        return False, "Password must include uppercase, lowercase, and a digit."
    if " " in password:
        return False, "Password cannot contain spaces."
    if username.lower() in password.lower():
        return False, "Password cannot contain your username."
    return True, "Password is valid."

# --------- Challenge 1: Password Strength Indicator
def check_password_strength(password: str) -> tuple[bool, str]:
    WEAK_PASSWORDS = ["password", "admin", "123456", "qwerty", "abc123", "welcome"]
    if any(pwd in password.lower() for pwd in WEAK_PASSWORDS):
        return False, "Weak password ❌: commonly used password."
    upper = any(c.isupper() for c in password)
    lower = any(c.islower() for c in password)
    digit = any(c.isdigit() for c in password)
    special = any(c in string.punctuation for c in password)
    points = sum([upper, lower, digit, special])
    if points < 3:
        return False, "Weak password ❌: must include uppercase, lowercase, digit, and special character."
    elif points == 3:
        return True, "Moderate password ⚠️: consider adding the missing type."
    else:
        return True, "Strong password ✅: good job!"

# --------- Challenge 3: Account Lockout
def add_failed_attempt(username: str):
    print(f"🚫 Too many failed attempts. Account locked for {ACCOUNT_LOCK_TIME // 60} minutes.")
    remaining = ACCOUNT_LOCK_TIME
    while remaining > 0:
        mins, secs = divmod(remaining, 60)
        print(f"\r🔒 Try again in {mins}m {secs}s", end="")
        time.sleep(1)
        remaining -= 1
    print("\n🔓 Account unlocked.")
    failed_attempts[username] = 0

# --------- Challenge 4: Session Management
def create_session(username: str) -> str:
    token = secrets.token_hex(16)
    with open(SESSION_FILE, 'a') as f:
        f.write(f"{username},{token}\n")
    print(f"🛡️ Session token created: {token}")
    return token

# --------- Menu Display
def display_menu():
    print("\n" + "="*60)
    print("🧠 MULTI-DOMAIN INTELLIGENCE PLATFORM 🧠".center(60))
    print("🔒 Secure Authentication System 🔒".center(60))
    print("="*60)
    print("[1] ✨ Register a new user")
    print("[2] 🔑 Login")
    print("[3] ❌ Exit")
    print("-"*60)

# --------- Main Loop
def main():
    while True:
        display_menu()
        choice = input("Select an option (1-3): ").strip()
        if choice == '1':
            username_attempts = 3
            while username_attempts > 0:
                username = input("Enter username: ").strip()
                valid, msg = validate_username(username)
                if not valid:
                    print(msg)
                    username_attempts -= 1
                    continue
                if user_exists(username):
                    print(f"Error: Username '{username}' already exists.")
                    username_attempts -= 1
                    continue
                password_attempts = 3
                while password_attempts > 0:
                    password = input("Enter password: ").strip()
                    valid, msg = validate_password(password, username)
                    if not valid:
                        print(msg)
                        password_attempts -= 1
                        continue
                    strong, msg = check_password_strength(password)
                    print(msg)
                    if not strong:
                        password_attempts -= 1
                        continue
                    password_confirm = input("Confirm password: ").strip()
                    if password != password_confirm:
                        print("Passwords do not match.")
                        password_attempts -= 1
                        continue
                    success, msg = register_user(username, password)
                    print(msg)
                    break
                break
        elif choice == '2':
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            success, msg = login_user(username, password)
            print(msg)
            if success:
                create_session(username)
                input("Press Enter to return to main menu...")
        elif choice == '3':
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid option. Choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
