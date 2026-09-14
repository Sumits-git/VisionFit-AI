import sqlite3
from pathlib import Path
from datetime import datetime

DB = Path(__file__).resolve().parent / 'tracker.db'

def ensure_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, exercise TEXT, reps INTEGER, duration REAL, timestamp TEXT)''')
    conn.commit()
    conn.close()

def log_session(exercise, reps, duration):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('INSERT INTO sessions (exercise, reps, duration, timestamp) VALUES (?,?,?,?)',
              (exercise, reps, duration, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def fetch_sessions():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT exercise, reps, duration, timestamp FROM sessions ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == '__main__':
    ensure_db()
    print('DB ready at', DB)
