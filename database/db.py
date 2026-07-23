"""
database/db.py

SQLite data-access layer for Spendly. No ORM — raw sqlite3 with
parameterized queries only.
"""

import os
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash

# Project root = one directory up from this file (database/ -> project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")

# Canonical list of valid expense categories. Single source of truth —
# import this wherever category options or validation are needed
# instead of re-typing the list.
CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    """
    Open a new connection to the Spendly SQLite database.

    - row_factory = sqlite3.Row so columns can be accessed by name
      (e.g. row["email"]).
    - PRAGMA foreign_keys = ON, since SQLite disables FK enforcement
      by default per-connection.

    Returns:
        sqlite3.Connection
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Create the users and expenses tables if they don't already exist.
    Safe to call on every app startup.
    """
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(conn, email):
    """
    Look up a single user by email.

    Returns:
        sqlite3.Row with columns (id, name, email, password_hash, created_at),
        or None if no user has that email.
    """
    return conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()


def get_user_by_id(conn, user_id):
    """
    Look up a single user by id.

    Returns:
        sqlite3.Row with columns (id, name, email, password_hash, created_at),
        or None if no user has that id.
    """
    return conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()


def get_expenses_by_user(conn, user_id):
    """
    Get all expenses for a user, ordered by date descending (newest first).

    Returns:
        list of sqlite3.Row objects with columns (id, user_id, amount, category,
        date, description, created_at).
    """
    return conn.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    ).fetchall()


def get_expense_by_id(conn, expense_id, user_id):
    """
    Look up a single expense by id, scoped to the owning user.

    Scoping by user_id in the WHERE clause ensures one user can never
    fetch (and therefore never edit) another user's expense, even if
    they guess or tamper with the id in the URL.

    Returns:
        sqlite3.Row with columns (id, user_id, amount, category, date,
        description, created_at), or None if no row exists with that
        id for that user.
    """
    return conn.execute(
        "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, user_id),
    ).fetchone()


def update_expense(conn, expense_id, user_id, amount, category, date, description):
    """
    Update an existing expense's editable fields.

    Scoped by user_id in the WHERE clause as defense-in-depth: even if
    a caller forgot to verify ownership beforehand, this statement can
    never modify a row belonging to a different user.

    Does NOT commit or close the connection. This follows the same
    convention as get_user_by_email(): functions that receive an
    already-open `conn` from the caller leave transaction/connection
    lifecycle to the caller (see register()'s INSERT + conn.commit()
    in app.py). Only functions that open their own connection
    internally via get_db() — init_db(), seed_db() — commit and close
    internally, because they own the connection's entire lifetime.

    Returns:
        int — rows affected (0 or 1). 0 means the row didn't exist or
        wasn't owned by this user at UPDATE time (caller may treat
        this the same as a 404).
    """
    cursor = conn.execute(
        """
        UPDATE expenses
        SET amount = ?, category = ?, date = ?, description = ?
        WHERE id = ? AND user_id = ?
        """,
        (amount, category, date, description, expense_id, user_id),
    )
    return cursor.rowcount


def seed_db():
    """
    Insert one demo user and 8 sample expenses — but only the first
    time this runs. If the users table already has rows, do nothing.
    """
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        if existing["count"] > 0:
            return

        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cursor.lastrowid

        today = datetime.now()
        year, month = today.year, today.month

        def day(d):
            return f"{year:04d}-{month:02d}-{d:02d}"

        sample_expenses = [
            (user_id, 45.50, "Food", day(2), "Groceries at Walmart"),
            (user_id, 25.00, "Transport", day(5), "Uber ride to work"),
            (user_id, 89.99, "Bills", day(8), "Electricity bill"),
            (user_id, 32.75, "Health", day(11), "Pharmacy - prescription refill"),
            (user_id, 15.99, "Entertainment", day(14), "Movie tickets"),
            (user_id, 120.00, "Shopping", day(18), "New running shoes"),
            (user_id, 10.00, "Other", day(22), "Miscellaneous purchase"),
            (user_id, 60.25, "Food", day(26), "Dinner at restaurant"),
        ]

        conn.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            sample_expenses,
        )
        conn.commit()
    finally:
        conn.close()
