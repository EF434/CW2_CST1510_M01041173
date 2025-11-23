'''
Name: Emaan Fatima
MISI: M01041173
Course:  CST1510 - Programming for Data Communication and Networks
CST1510 Week 7 Lab: Secure Authentication System
'''

# --------- Step 3 - Import Required Modules
import bcrypt
import os
from pathlib import Path
import string # Challenge 1: Password strength
import re # For Input Validation
import time # Challenge 3: Account lockout
import secrets # Challenge 4: Session management

# ---------  Step 6. Define Constants & Files
# Define paths
DATA_DIR = Path("DATA")       
USER_DATA_FILE = DATA_DIR / "users.txt"
SESSION_FILE = DATA_DIR / "sessions.txt" # For Challenge 4
MAX_ATTEMPTS = 3 # Maximum login attempts
ACCOUNT_LOCK_TIME = 300  # 5 minutes lockout time (seconds)

#  ---------Dictionary to track failed attempts
failed_attempts = {} # Challenge 3

# --------- Step 4 - Implement the Password Hashing Function
def hash_password(plain_text_password: str) -> str:
    '''
    Hashes a password using bcrypt with automatic salt generation.

    Args:
      plain_text_password (str): The plaintext password to hash

    Returns:
      str: The hashed password as a UTF-8 string
    '''
    # Encode the password to bytes (bcrypt requires byte strings)
    password_bytes = plain_text_password.encode('utf-8')

    # Generate a salt using bcrypt.gensalt()
    salt = bcrypt.gensalt()

    # Hash the password using bcrypt.hashpw()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    # Decode the hash back to a string to store in a text file
    return hashed_password.decode('utf-8')

# --------- Step 5 - Implement the Password Verification Function
def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    '''
    Verifies a plaintext password against a stored bcrypt hash.

    Args:
       plain_text_password (str): The password to verify
       hashed_password (str): The stored hash to check against

    Returns:
       bool: True if the password matches, False otherwise

    '''
    # Encode both the plaintext password and the stored hash to bytes
    password_bytes = plain_text_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')

    # Use try-except to handle potential errors during verification
    # Use bcrypt.checkpw() to verify the password
    try:
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    
    except ValueError:
        print("Error: Invalid hash format.")
        return False
    
    except Exception as e:
        print(f"Error during password verification: {e}")
        return False

# --------- Step 6. Test Your Hashing Functions

#====================
# TEMPORARY TEST CODE
#====================
# Sample password for testing
# - test_password = "SecurePassword123"

# Test hashing
# - hashed = hash_password(test_password)
# - (f"Original password: {test_password}")
# - print(f"Hashed password: {hashed}")
# - print(f"Hash length: {len(hashed)} characters")

# Test verification with correct password
# - is_valid = verify_password(test_password, hashed)
# - (f"\nVerification with correct password: {is_valid}")

# Test verification with incorrect password
# - is_invalid = verify_password("WrongPassword", hashed)
# - print(f"Verification with incorrect password: {is_invalid}")


# --------- Step 8. Implement the User Existence Check
def user_exists(username: str) -> bool:
    '''
    Checks if a username already exists in the user database. 

    Args:
      username (str): The username to check

    Returns:
      bool: True if the user exists, False otherwise
    '''
    # Handle the case where the file doesn't exist yet
    if not os.path.exists(USER_DATA_FILE):
        return False
    
    # Read the file and check each line for the username
    try:
        with open(USER_DATA_FILE, "r") as f:
            # Read each line and compare stored username with input
            for line in f:
                saved_username = line.strip().split(",")[0]
                if username.lower() == saved_username.lower(): # Case-insensitive check
                    return True
                
    # Error handling to prevent crashes          
    except Exception as e:
        print(f"Error checking user existence: {e}")
    return False

# --------- Step 7. Implement the Registration Function
def register_user(username: str, password: str, role: str = None) -> bool:
    '''
    Registers a new user by hashing their password and storing credentials.

    Args:
       username (str): The username for the new account
       password (str): The plaintext password to hash and store

    Returns:
       bool: True if registration successful, False if username already exists

    Challenge 2:
       Register a user with a specific role (user, admin, analyst).


    '''    
    # Check if the username already exists
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False
    
    # Hash the password
    hashed_password = hash_password(password)

    # --- Challenge 2: User Role System
    # Validate role input
    available_roles = ["user", "admin", "analyst"]

    # Available roles
    available_roles = ["user", "admin", "analyst"]

    # Use provided role if valid
    if role and role.lower() in available_roles:
        role = role.lower()
    else:
        # Fallback to default role
        role = "user"

    # Append the new user to the file
    # Format: username, hashed_password, role (updated format for Challenge 2)
    try:
        # Open the file in append mode or create if it doesn't exist
        with open(USER_DATA_FILE, "a") as f:
            f.write(f"{username},{hashed_password},{role}\n") 
        print(f"User '{username}' - {role} registered")
        return True 
    
    # Error handling to prevent crashes
    except Exception as e:
        print(f"Error registering user: {e}")
        return False
    

# --------- Step 9, Implement the Login Function

def login_user(username, password):
    '''
    Authenticates a user by verifying their username and password.

    Args:
        username (str): The username to authenticate
        password (str): The plaintext password to verify

    Returns:
        bool: True if authentication successful, False otherwise
    '''

    # Handle the case where the file doesn't exist yet
    if not os.path.exists(USER_DATA_FILE):
        return "⚠️ No users registered yet."
    
    # Initialize failed attempts for the user if not present
    if username not in failed_attempts:
        failed_attempts[username] = 0
    
    # Check if account is locked
    if failed_attempts[username] >= MAX_ATTEMPTS:
        return f"🚫 Account is locked. Please wait {ACCOUNT_LOCK_TIME // 60} minutes before trying again."
    
    # Read the user data file
    try:
        # Open the user data file
        with open(USER_DATA_FILE) as f:
            # Check each line for the username
            username_found = False
            for line in f.readlines():
                # Split line into username, hash, and role
                user, hash, role = line.strip().split(',', 2)

                # If username matches, verify the password
                if user == username:
                    username_found = True

                    # Verify the password
                    if verify_password(password, hash):
                        failed_attempts[username] = 0  # Reset on successful login
                        return True
                  
                    failed_attempts[username] += 1
                    remaining_attempts = MAX_ATTEMPTS - failed_attempts[username]
                    if remaining_attempts > 0:
                        return f"❌ Incorrect password. Attempts used: {failed_attempts[username]}. Attempts remaining: {remaining_attempts}"
                    else:
                        add_failed_attempt(username)
        

        # Username not found after checking all lines
        if not username_found:
            return "❌ Username not found."

    except FileNotFoundError:
        print("⚠️ No users registered yet.")
        return False

    except Exception as e:
        print(f"Error during login: {e}")
        return False


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



# ========== Challenge Section:  Implementing additional features: ==========

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
    
# == Challenge 3: Account Lockout ==
def add_failed_attempt(username):
    """Implement a system that locks accounts after 3 failed login attempts:"""

    print("🚫 Too many failed attempts. Account locked for 5 minutes.")

    # Countdown timer for lockout
    remaining_time = ACCOUNT_LOCK_TIME

    # Display countdown
    while remaining_time > 0:
        # Calculate minutes and seconds
        minutes = remaining_time // 60
        seconds = remaining_time % 60

        # Display remaining_time time
        print(f"\r🔒 Try again in {minutes}m {seconds}s", end="")

        # Wait for 1 second
        time.sleep(1)

        # Decrement remaining time
        remaining_time -= 1

    # Unlock message
    print("\n🔓 Account unlocked. You can try logging in again.")
    failed_attempts[username] = 0  # Reset after lockout

    return True # Account unlocked


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

def display_menu():
        # Decorative header
        print("\n" + "="*60)
        print("🧠 MULTI-DOMAIN INTELLIGENCE PLATFORM 🧠".center(60))
        print("🔒 Secure Authentication System 🔒".center(60))
        print("="*60 + "\n")

        # Menu options with icons
        menu = ["[1] ✨ Register a new user", "[2] 🔑 Login", "[3] ❌ Exit"]

        # Display menu
        for options in menu:
            print(options)
        print("-"*60)

def main():

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        # ----- Registration flow
        if choice == '1':
            print("\n--- USER REGISTRATION ---")

            # Registration username input with 3 attempts
            username_attempts = 3
            while username_attempts > 0:

                # Get username input
                username = input("Enter a username: ").strip()

                # Validate username
                is_valid, error_msg = validate_username(username)
                if not is_valid:
                    print(f"Error: {error_msg}")
                    username_attempts -= 1
                    print(f"Username attempts remaining: {username_attempts}")
                    continue

                # Check if username already exists
                if user_exists(username):
                    print(f"Error: Username '{username}' already exists.")
                    username_attempts -= 1
                    print(f"Username attempts remaining: {username_attempts}")
                    continue

                # Password attempts
                password_attempts = 3
                while password_attempts > 0:

                    # Get password input
                    password = input("Enter a password: ").strip()

                    # Validate password
                    is_valid, error_msg = validate_password(password, username)
                    if not is_valid:
                        print(f"Error: {error_msg}")
                        password_attempts -= 1
                        print(f"Password attempts remaining: {password_attempts}")
                        continue

                    # Challenge 1: Check password strength
                    is_strong, msg = check_password_strength(password)
                    print(msg)
                    if msg.startswith("Moderate"):
                        user_choice = input("Do you want to proceed with this password? (y/n): ").strip().lower()
                        if user_choice != 'y':
                            password_attempts -= 1
                            print(f"Password attempts remaining: {password_attempts}")
                            continue
                    elif not is_strong: 
                        password_attempts -= 1
                        print(f"Password attempts remaining: {password_attempts}")
                        continue

                    # Confirm password
                    password_confirm = input("Confirm password: ").strip()
                    if password != password_confirm:
                        print("Error: Passwords do not match.")
                        password_attempts -= 1
                        print(f"Password attempts remaining: {password_attempts}")
                        continue

                    # Register the user
                    if register_user(username, password):
                        print(f"Success: User '{username}' registered successfully!")
                    break  # Exit password loop

                else:
                    print("❌ Maximum password attempts reached. Returning to main menu.")
                    break  # Exit username loop

                break  # Exit username loop if registration succeeded

            else:
                print("❌ Maximum username attempts reached. Returning to main menu.")

        # -----  Attempt Login 
        elif choice == '2':
            # Logic flow for user login
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
 
            while True:
                # Get password input
                password = input("Enter your password: ").strip()

                # Attempt login
                login_status = login_user(username, password)

                # Check login status
                if login_status is True:
                    print("\nYou are now logged in.")
                    print("(In a real application, you would now access the main dashboard)")

                    # Create session token
                    create_session(username)

                    # Optional: Ask if they want to logout or exit
                    input("\nPress Enter to return to main menu...")
                    break
                else:
                    # Display login status message
                    print(login_status)
                    
                    # Break loop if account is locked or username not found
                    if "locked" in str(login_status) or "not found" in str(login_status):
                        break
        
                    
        # ----- Exit
        elif choice == '3':
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        # ----- Invalid Option 
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()