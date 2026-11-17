import os
import sqlite3

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "expense_tracker.db"))

CREATE_USERS_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

CREATE_EXPENSES_SQL = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'Food', 'Transport', 'Bills', 'Health',
        'Entertainment', 'Shopping', 'Other'
    )),
    date TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

SEED_EXPENSES = [
    (12.50, "Food", "2026-09-02", "Coffee and bagel"),
    (45.00, "Transport", "2026-09-04", "Monthly bus pass"),
    (89.99, "Bills", "2026-09-05", "Electricity bill"),
    (60.00, "Health", "2026-09-09", "Pharmacy - prescription"),
    (15.00, "Entertainment", "2026-09-13", "Movie ticket"),
    (120.00, "Shopping", "2026-09-18", "New running shoes"),
    (25.00, "Other", "2026-09-22", "Birthday gift"),
    (32.75, "Food", "2026-09-27", "Groceries"),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.executescript(CREATE_USERS_SQL + CREATE_EXPENSES_SQL)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        already_seeded = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0
        if already_seeded:
            return

        password_hash = generate_password_hash("demo123")
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cur.lastrowid

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            [(user_id, *row) for row in SEED_EXPENSES],
        )
        conn.commit()
    finally:
        conn.close()
