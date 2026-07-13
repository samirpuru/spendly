#!/usr/bin/env python3
"""
seed_single_user.py

Create a single dummy Indian user in the database.
"""

import random
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_db
from werkzeug.security import generate_password_hash

# Indian names across regions
FIRST_NAMES = [
    "Rahul", "Priya", "Arjun", "Ananya", "Vikram", "Sneha", "Aditya",
    "Pooja", "Rohan", "Divya", "Amit", "Shreya", "Harshit", "Neha",
    "Sanjay", "Kavya", "Nikhil", "Pallavi", "Rohit", "Tanvi", "Varun",
    "Ishita", "Aman", "Diya", "Karan", "Zara", "Manish", "Sakshi"
]

LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Gupta", "Kumar", "Reddy", "Nair",
    "Verma", "Kapoor", "Malhotra", "Mishra", "Bhat", "Iyer", "Menon",
    "Desai", "Rao", "Chopra", "Sinha", "Mahajan", "Saxena", "Joshi",
    "Pandey", "Yadav", "Chaudhary", "Thakur", "Bose", "Roy"
]

def generate_unique_user():
    """Generate a unique Indian user until email doesn't already exist."""
    conn = get_db()
    try:
        while True:
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            name = f"{first_name} {last_name}"

            # Generate email: lowercase name + random 2-3 digit suffix
            suffix = random.randint(10, 999)
            email = f"{first_name.lower()}.{last_name.lower()}{suffix}@gmail.com"

            # Check if email already exists
            existing = conn.execute(
                "SELECT COUNT(*) AS count FROM users WHERE email = ?",
                (email,)
            ).fetchone()

            if existing["count"] == 0:
                # Email is unique
                return name, email
    finally:
        conn.close()


def seed_single_user():
    """Insert a single random Indian user into the database."""
    # Generate unique user
    name, email = generate_unique_user()

    # Hash password
    password_hash = generate_password_hash("password123")

    # Insert into database
    conn = get_db()
    try:
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (name, email, password_hash),
        )
        conn.commit()
        user_id = cursor.lastrowid

        # Print confirmation
        print("User created successfully!")
        print(f"  id: {user_id}")
        print(f"  name: {name}")
        print(f"  email: {email}")

    finally:
        conn.close()


if __name__ == "__main__":
    seed_single_user()
