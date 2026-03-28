import sqlite3
import hashlib
import bcrypt
import uuid


# ================= CONNECTION =================
def connect():
    return sqlite3.connect("users.db", check_same_thread=False)


# ================= INIT DATABASE =================
def init_db():
    conn = connect()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            profile_image TEXT
        )
    """)

    # Chats table
    c.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            username TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Messages table
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             chat_id TEXT,
             username TEXT,
             role TEXT,
             content TEXT,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       )
    """)




# ================= USER AUTH =================
def register(username, password):
    username = username.lower()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = connect()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login(username, password):
    username = username.lower()

    conn = connect()
    c = conn.cursor()

    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        stored_password = result[0]
        if bcrypt.checkpw(password.encode(), stored_password):
            return True

    return False


# ================= CHAT SYSTEM =================
def create_chat(username):
    chat_id = str(uuid.uuid4())

    conn = connect()
    c = conn.cursor()

    c.execute(
        "INSERT INTO chats (id, username) VALUES (?, ?)",
        (chat_id, username),
    )

    conn.commit()
    conn.close()
    return chat_id


def get_user_chats(username):
    conn = connect()
    c = conn.cursor()

    c.execute(
        "SELECT id FROM chats WHERE username=? ORDER BY created_at DESC",
        (username,),
    )

    chats = c.fetchall()
    conn.close()
    return [chat[0] for chat in chats]


def delete_chat(chat_id):
    conn = connect()
    c = conn.cursor()

    c.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
    c.execute("DELETE FROM chats WHERE id=?", (chat_id,))

    conn.commit()
    conn.close()


# ================= MESSAGE SYSTEM =================
def save_message(username, chat_id, role, content):
    conn = connect()
    c = conn.cursor()

    c.execute(
        "INSERT INTO messages (chat_id, username, role, content) VALUES (?, ?, ?, ?)",
        (chat_id, username, role, content)
    )

    conn.commit()
    conn.close()


def load_messages(username, chat_id):
    conn = connect()
    c = conn.cursor()

    c.execute(
        "SELECT role, content, created_at FROM messages WHERE username=? AND chat_id=? ORDER BY id ASC",
        (username, chat_id)
    )

    data = c.fetchall()
    conn.close()
    return data


# ================= PROFILE IMAGE =================
def save_profile_image(username, image_base64):
    conn = connect()
    c = conn.cursor()

    c.execute(
        "UPDATE users SET profile_image=? WHERE username=?",
        (image_base64, username)
    )

    conn.commit()
    conn.close()


def get_profile_image(username):
    conn = connect()
    c = conn.cursor()

    c.execute(
        "SELECT profile_image FROM users WHERE username=?",
        (username,)
    )

    result = c.fetchone()
    conn.close()

    return result[0] if result and result[0] else None