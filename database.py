import sqlite3

conn = sqlite3.connect("campus.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
email TEXT UNIQUE,
password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
resource TEXT,
date TEXT,
time TEXT,
members INTEGER,
status TEXT
)
""")
# ADMIN TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

# Default admin
cursor.execute("""
INSERT OR IGNORE INTO admin(id,username,password)
VALUES(1,'admin','admin123')
""")
# Paste These Routes in `app.py`=
cursor.execute("""
CREATE TABLE IF NOT EXISTS resources(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    location TEXT NOT NULL
)
""")
conn.commit()
conn.close()

print("Database Created Successfully")