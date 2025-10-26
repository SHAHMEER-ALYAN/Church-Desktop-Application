import hashlib
from database.db_connection import get_connection

def hash_password(password):
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def authenticate_user(username, password):
    """Return user data if credentials are correct."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    # Verify password
    if user['password_hash'] == hash_password(password):
        return user
    else:
        return None

def create_user(username, password, full_name, role='staff'):
    """Create a new user with hashed password."""
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, role)
        VALUES (%s, %s, %s, %s)
    """, (username, hashed, full_name, role))
    conn.commit()
    conn.close()


