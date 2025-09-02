from database import get_db

def log_event(username, status):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (username, status) VALUES (?, ?)", (username, status))
    conn.commit()
    conn.close()
