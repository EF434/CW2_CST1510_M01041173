"""
users.py - Provide helper functions for managing user in daabase

"""

# Get a user record based on username
def get_user_by_username(conn, username):
    """Retrieve user by username."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        user = cursor.fetchone()
        return user
    
    except Exception as e:
        print(f"❌ Error retrieving user '{username}': {e}")
        return None


# Add a new user to the database
def insert_user(conn, username, password_hash, role='user'):
    """Insert new user."""

    # Error handling to prevent crashes 
    try:
        cursor = conn.cursor()
        cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
         )
        return True
    except Exception as e:
         print(f"⚠️ Error occurred inserting user '{username}': {e}")
         return False
