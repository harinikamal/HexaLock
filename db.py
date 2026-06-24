# db.py
import sqlite3
import time

DB_NAME = "hexalock.db"


# ---------------- INIT DATABASE ----------------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS access_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        action TEXT,
                        user TEXT,
                        timestamp REAL
                    )''')

        c.execute('''CREATE TABLE IF NOT EXISTS otps (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        otp TEXT,
                        recipient TEXT,
                        filename TEXT,
                        expiry REAL
                    )''')

        # Index for faster lookup
        c.execute('''CREATE INDEX IF NOT EXISTS idx_otp_lookup 
                     ON otps (otp, recipient, filename)''')


# ---------------- LOG ACCESS ----------------
def log_access(filename, action, user):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO access_logs (filename, action, user, timestamp) VALUES (?, ?, ?, ?)",
            (filename, action, user, time.time())
        )


# ---------------- STORE OTP ----------------
def store_otp(otp, recipient, filename, ttl_seconds):
    expiry_time = time.time() + ttl_seconds

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO otps (otp, recipient, filename, expiry) VALUES (?, ?, ?, ?)",
            (otp, recipient, filename, expiry_time)
        )


# ---------------- VALIDATE OTP ----------------
def validate_and_consume_otp(otp, recipient, filename):
    current_time = time.time()

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # Clean expired OTPs
        c.execute("DELETE FROM otps WHERE expiry < ?", (current_time,))

        # Check OTP
        c.execute(
            "SELECT id FROM otps WHERE otp=? AND recipient=? AND filename=?",
            (otp, recipient, filename)
        )
        row = c.fetchone()

        if row:
            # Delete after successful use
            c.execute("DELETE FROM otps WHERE id=?", (row[0],))
            return True

    return False


# ---------------- FETCH LOGS ----------------
def get_recent_logs(limit=10):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT filename, action, user, timestamp FROM access_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return c.fetchall()
