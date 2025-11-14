# --------- Step 3 - Import Required Modules
import bcrypt
import os

'''
Name: Emaan Fatima
MISI: M01041173
Course:  CST1510 - Programming for Data Communication and Networks
CST1510 Week 7 Lab: Secure Authentication System
'''
# --------- Step 3 - Import Required Modules
import bcrypt
import os
# Import additional modules
import string
import re


>>>>>>> 8606265 (Updates week 7 files)
# ---------  Step 6. Define the User Data File
USER_DATA_FILE = "users.txt"

# --------- Step 4 - Implement the Password Hashing Function
<<<<<<< HEAD
def hash_password(plain_text_password):
    # TODO: Encode the password to bytes (bcrypt requires byte strings)
    password_bytes = plain_text_password.encode('utf-8')
    # TODO: Generate a salt using bcrypt.gensalt()
    salt = bcrypt.gensalt()
    # TODO: Hash the password using bcrypt.hashpw()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    # TODO: Decode the hash back to a string to store in a text file
    return hashed_password.decode('utf-8')

# --------- Step 5 - Implement the Password Verification Function
def verify_password(plain_text_password, hashed_password):
    # TODO: Encode both the plaintext password and the stored hash to bytes
    password_bytes = plain_text_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    # TODO: Use bcrypt.checkpw() to verify the password
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    # This function extracts the salt from the hash and compares

# --------- Step 6. Test Your Hashing Functions
# Done

# --------- Step 7. Implement the Registration Function
def register_user(username, password):
    # TODO: Check if the username already exists
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False
    # TODO: Hash the password
    hashed_password = hash_password(password)
    # TODO: Append the new user to the file
    # Format: username,hashed_password
    with open("users.txt", "a") as f:
        f.write(f"{username},{hashed_password}\n") 
    print(f"User '{username}' registered.")
    return True 

# --------- Step 8. Implement the User Existence Check
def user_exists(username):
    # TODO: Handle the case where the file doesn't exist yet
    if not os.path.exists(USER_DATA_FILE):
        return False 
    # TODO: Read the file and check each line for the username
    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            if line.startswith(username + ","):
                return True
    return False

# --------- Step 9. Implement the Login Function
def login_user(username, password): 
   # TODO: Handle the case where no users are registered yet
   if os.path.isfile(USER_DATA_FILE) == False:
    return False
   # TODO: Search for the username in the file
   with open("users.txt", "r") as f:
    for line in f.readlines():
        user, hash = line.strip().split(',', 1)
        # TODO: If username matches, verify the password
        if user == username:
            return verify_password(password, hash)
  # TODO: If we reach here, the username was not found
   return False

# --------- Step10. Implement Input Validation
def validate_username(username):
    if not username:
        print("Username cannot be empty.")
        return False
    if len(username) < 5:
        return False, "Username must be at least 5 characters long."
    return True, ""  


def validate_password(password):
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""
=======
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
    # Check for empty or whitespace-only input
    if not plain_text_password.strip() or not hashed_password.strip():
        raise ValueError("Invalid input: password and hashed password cannot be blank or whitespace only.")

    # Encode both the plaintext password and the stored hash to bytes
    password_bytes = plain_text_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')

    # Use bcrypt.checkpw() to verify the password
    # Perform password check while managing exceptions to avoid crashes
    try:
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
        # This function extracts the salt from the hash and compares
    except ValueError:
        print("Error: Invalid hash format.")
        return False
    
    except Exception as e:
        print(f"Error during password verification: {e}")
        return False

# --------- Step 6. Test Your Hashing Functions
'''
====================
TEMPORARY TEST CODE
====================
# Sample password for testing
- test_password = "SecurePassword123"

# Test hashing
- hashed = hash_password(test_password)
- (f"Original password: {test_password}")
- print(f"Hashed password: {hashed}")
- print(f"Hash length: {len(hashed)} characters")

# Test verification with correct password
- is_valid = verify_password(test_password, hashed)
- (f"\nVerification with correct password: {is_valid}")

# Test verification with incorrect password
- is_invalid = verify_password("WrongPassword", hashed)
- print(f"Verification with incorrect password: {is_invalid}")

'''

# --------- Step 7. Implement the Registration Function
def register_user(username: str, password: str) -> tuple[bool, str]:
    '''
    Registers a new user by hashing their password and storing credentials.

     Args:
     username (str): The username for the new account
     password (str): The plaintext password to hash and store

     Returns:
       bool: True if registration successful, False if username already exists

    '''
    # Check for empty or whitespace-only input
    if not username.strip() or not password.strip():
        return False, "Username and password cannot be empty."
    
    # Check if the username already exists
    if user_exists(username):
        return False, f"Error: Username '{username}' already exists."
    
    # Hash the password
    hashed_password = hash_password(password)

    # Append the new user to the file
    # Format: username,hashed_password
    try:
        with open("users.txt", "a") as f:
            f.write(f"{username},{hashed_password}\n") 
            print(f"User '{username}' registered.")
        return True 
    
    except ValueError:
        print("Error: Invalid input for registration.")
        return False
    
    except Exception as e:
        print(f"Error during user registration: {e}")
        return False
    

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
       return False, f"{USER_DATA_FILE} does not exist."
    
    # Read the file and compare stored usernames
    # Error handling to prevent crashes
    try:
        with open(USER_DATA_FILE, "r") as f:
            # Read each line and compare stored username with input
            for line in f:
                saved_username = line.strip().split(":")[0]
                if username == saved_username:
                    return True
                
    except Exception as e:
        print(f"Error checking user existence: {e}")
    
    return False

# --------- Step9, Implement the Login Function
def login_user(username, password): 
   '''
   Authenticates a user by verifying their username and password.

   Args:
     username (str): The username to authenticate
     password (str): The plaintext password to verify
 
    Returns:
    bool: True if authentication successful, False otherwise
   '''

   # Handle the case where no users are registered yet
   if not os.path.exists(USER_DATA_FILE):
    return False, "⚠️ No users registered yet."
   
   # Search for the username in the file
 
   try:
    with open(USER_DATA_FILE) as f:
        for line in f.readlines():
            user, hash = line.strip().split(',', 1)

            # If username matches, verify the password
            if user == username:
                if verify_password(password, hash):
                    return True, f"✅ Login successful! Welcome, {username}."
                else:
                    return False, "❌ Invalid username or password."

    # If we reach here, the username was not found
    return False, "Invalid username or password."

   except ValueError:
    print("Error: Invalid input for login.")

   except Exception as e:
    print(f"Error during login: {e}")
    return False, " ⚠️ An error occurred during login."


# --------- Step10. Implement Input Validation
def validate_username(username):
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
    if username.isdigit():
        return False, "Username cannot be entirely numeric."
    
    # Check for spaces in username
    if ' ' in username:
        return False, "Username cannot contain spaces."
    
    return True, "Username is valid."


def validate_password(password):
    symbols = string.punctuation
    # Check length
    if len(password) < 6 or len(password) > 50:
        return False, "Password must be between 6 and 50 characters long."

    # Check letters and digits with regex
    if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password) and re.search(r"\d", password):
        return False, "Password must contain at least one uppercase letter, one lowercase letter, and one digit."
    
    return True, ""             
>>>>>>> 8606265 (Updates week 7 files)

# --------- Step 11. Implement the Main Menu
def display_menu():
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            password = input("Enter a password: ").strip()

            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            if register_user(username, password):
                print(f"Success: User '{username}' registered successfully!")

        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # Attempt login
            if login_user(username, password):
                print(f"Success: Welcome, {username}!")
                # Optional: Ask if they want to logout or exit
                input("\nPress Enter to return to main menu...")
            else:
                print("Error: Invalid username or password.")

        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
