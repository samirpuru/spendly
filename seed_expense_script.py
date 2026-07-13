"""
Seed expenses for a specific user.
Usage: python seed_expense_script.py <user_id> <count> <months>
"""
import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta

# Set up database path using the same pattern as db.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")


def get_db():
    """Open connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def seed_expenses(user_id, count, months):
    """
    Generate and insert <count> expenses for <user_id>
    spread across the past <months> months.
    """
    conn = get_db()
    try:
        # Verify user exists
        user = conn.execute(
            "SELECT id, name FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        if not user:
            print(f"Error: No user found with id {user_id}")
            return False

        print(f"[OK] User found: {user['name']} (id={user['id']})")

        # Category distribution and amounts (in Rupees, realistic for India)
        categories_amounts = {
            "Food": (50, 800),        # Most common
            "Transport": (20, 500),
            "Bills": (200, 3000),
            "Health": (100, 2000),    # Least common
            "Entertainment": (100, 1500),
            "Shopping": (200, 5000),
            "Other": (50, 1000),
        }

        # Weight categories: Food more common, Health/Entertainment less
        weighted_categories = (
            ["Food"] * 4 +
            ["Shopping"] * 2 +
            ["Transport"] * 2 +
            ["Bills"] * 2 +
            ["Other"] * 2 +
            ["Health"] * 1 +
            ["Entertainment"] * 1
        )

        # Generate expenses spread across past <months> months
        expenses = []
        today = datetime.now()

        for _ in range(count):
            # Random day in the past <months> months
            days_back = random.randint(0, months * 30)
            expense_date = today - timedelta(days=days_back)
            date_str = expense_date.strftime("%Y-%m-%d")

            # Pick a random category
            category = random.choice(weighted_categories)
            min_amount, max_amount = categories_amounts[category]
            amount = round(random.uniform(min_amount, max_amount), 2)

            # Description based on category
            descriptions = {
                "Food": ["Groceries", "Restaurant meal", "Food delivery", "Cafe"],
                "Transport": ["Auto/Taxi ride", "Bus fare", "Petrol", "Parking"],
                "Bills": ["Electricity", "Water bill", "Internet", "Phone bill"],
                "Health": ["Doctor visit", "Medicines", "Dentist", "Gym"],
                "Entertainment": ["Movie ticket", "Streaming subscription", "Gaming"],
                "Shopping": ["Clothing", "Electronics", "Books", "Home items"],
                "Other": ["Miscellaneous", "Tips", "Donations"],
            }
            description = random.choice(descriptions.get(category, ["Expense"]))

            expenses.append((user_id, amount, category, date_str, description))

        # Insert all expenses in a single transaction
        try:
            conn.executemany(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                expenses
            )
            conn.commit()
            print(f"[OK] Inserted {count} expenses")
        except Exception as e:
            conn.rollback()
            print(f"Error inserting expenses: {e}")
            return False

        # Fetch and display the inserted expenses
        inserted = conn.execute(
            """
            SELECT id, amount, category, date, description
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 5
            """,
            (user_id,)
        ).fetchall()

        if inserted:
            dates = [exp["date"] for exp in inserted]
            min_date = min(dates)
            max_date = max(dates)
            print(f"\nDate range: {min_date} to {max_date}")
            print(f"\nSample of inserted expenses:")
            print("-" * 70)
            for exp in inserted:
                print(
                    f"  #{exp['id']:3d} | Rs {exp['amount']:7.2f} | {exp['category']:15s} | "
                    f"{exp['date']} | {exp['description']}"
                )
            print("-" * 70)

        return True

    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python seed_expense_script.py <user_id> <count> <months>")
        print("Example: python seed_expense_script.py 1 50 6")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("Error: Arguments must be integers")
        print("Usage: python seed_expense_script.py <user_id> <count> <months>")
        sys.exit(1)

    success = seed_expenses(user_id, count, months)
    sys.exit(0 if success else 1)
