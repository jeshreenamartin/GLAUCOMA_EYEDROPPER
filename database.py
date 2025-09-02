import sqlite3
import os

def init_db():
    # Ensure the database directory exists
    db_dir = os.path.dirname(os.path.abspath("eyedrop.db"))
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect("eyedrop.db")
    cur = conn.cursor()

    # Users table
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')

    # Logs table
    cur.execute('''CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect("eyedrop.db", check_same_thread=False)
    return conn

# Call init on startup
init_db()