# --------- Step 3 - Import Required Modules
import bcrypt
import os
# ---------  Step 6. Define the User Data File
USER_DATA_FILE = "users.txt"

# --------- Step 4 - Implement the Password Hashing Function
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
