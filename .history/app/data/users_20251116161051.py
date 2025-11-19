# users.py contains helper functions for managing user data in the database

# Imports 
from app.data.db import connect_database

# Get a user record based on username
def get_user_by_username(username):
    """Retrieve user by username."""
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?))
        user = cursor.fetchone()
        conn.close()
        return user
    
    except Exception as e:
        print(f"❌ Error retrieving user '{username}': {e}")
        return None


# Add a new user to the database
def insert_user(username, password_hash, role='user'):
    """Insert new user."""

    # Error handling to prevent crashes 
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
         )
        conn.commit()
        return True
    except Exception as e:
         print(f"⚠️ Error occurred inserting user '{username}': {e}")
         return False
