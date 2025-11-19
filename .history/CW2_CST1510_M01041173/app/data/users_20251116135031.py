# users.py contains helper functions for managing user data in the database

# Imports 
from app.data.db import connect_database

# Get a user record based on username
def get_user_by_username(username):
    """Retrieve user by username."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

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
         print(f"⚠️ Error inserting user '{username}': {e}")
        return False
    conn.close()