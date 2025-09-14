# db.py
import sqlite3
import time

DB_NAME = "hexalock.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    action TEXT,
                    user TEXT,
                    timestamp REAL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS otps (
                    otp TEXT,
                    recipient TEXT,
                    filename TEXT,
                    expiry REAL
                )''')
    conn.commit()
    conn.close()

def log_access(filename, action, user):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO access_logs (filename, action, user, timestamp) VALUES (?, ?, ?, ?)",
              (filename, action, user, time.time()))
    conn.commit()
    conn.close()

def store_otp(otp, recipient, filename, ttl_seconds):
    expiry_time = time.time() + ttl_seconds
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO otps (otp, recipient, filename, expiry) VALUES (?, ?, ?, ?)",
              (otp, recipient, filename, expiry_time))
    conn.commit()
    conn.close()

def validate_and_consume_otp(otp, recipient, filename):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT expiry FROM otps WHERE otp=? AND recipient=? AND filename=?", (otp, recipient, filename))
    row = c.fetchone()
    if row:
        expiry = row[0]
        if time.time() < expiry:
            c.execute("DELETE FROM otps WHERE otp=? AND recipient=? AND filename=?", (otp, recipient, filename))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False

def get_recent_logs(limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT filename, action, user, timestamp FROM access_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    logs = c.fetchall()
    conn.close()
    return logs
