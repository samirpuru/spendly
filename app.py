from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db, get_user_by_email

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Decorators                                                          #
# ------------------------------------------------------------------ #

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        error = None
        if not name:
            error = "Please enter your full name."
        elif not email or "@" not in email or "." not in email.split("@")[-1]:
            error = "Please enter a valid email address."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        elif password != confirm_password:
            error = "Passwords do not match."

        if error is None:
            conn = get_db()
            try:
                existing = get_user_by_email(conn, email)
                if existing is not None:
                    error = "An account with this email already exists."
                else:
                    password_hash = generate_password_hash(password)
                    try:
                        conn.execute(
                            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                            (name, email, password_hash),
                        )
                        conn.commit()
                    except sqlite3.IntegrityError:
                        error = "An account with this email already exists."
            finally:
                conn.close()

            if error is None:
                return redirect(url_for("login"))

        return render_template("register.html", error=error, name=name, email=email)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        error = None
        if not email:
            error = "Please enter your email address."
        elif not password:
            error = "Please enter your password."

        if error is None:
            conn = get_db()
            try:
                user = get_user_by_email(conn, email)
            finally:
                conn.close()

            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Invalid email or password."
            else:
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                return redirect(url_for("profile"))

        return render_template("login.html", error=error, email=email)

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "January 2026",
    }
    stats = {
        "total_spent": "₹399.48",
        "transaction_count": 8,
        "top_category": "Shopping",
    }
    transactions = [
        {"date": "26 Jul 2026", "description": "Dinner at restaurant", "category": "Food", "amount": "₹60.25"},
        {"date": "22 Jul 2026", "description": "Miscellaneous purchase", "category": "Other", "amount": "₹10.00"},
        {"date": "18 Jul 2026", "description": "New running shoes", "category": "Shopping", "amount": "₹120.00"},
        {"date": "14 Jul 2026", "description": "Movie tickets", "category": "Entertainment", "amount": "₹15.99"},
        {"date": "11 Jul 2026", "description": "Pharmacy - prescription refill", "category": "Health", "amount": "₹32.75"},
        {"date": "08 Jul 2026", "description": "Electricity bill", "category": "Bills", "amount": "₹89.99"},
        {"date": "05 Jul 2026", "description": "Uber ride to work", "category": "Transport", "amount": "₹25.00"},
        {"date": "02 Jul 2026", "description": "Groceries at Walmart", "category": "Food", "amount": "₹45.50"},
    ]
    categories = [
        {"name": "Shopping", "amount": "₹120.00", "percent": 30, "slug": "shopping"},
        {"name": "Food", "amount": "₹105.75", "percent": 25, "slug": "food"},
        {"name": "Bills", "amount": "₹89.99", "percent": 20, "slug": "bills"},
        {"name": "Health", "amount": "₹32.75", "percent": 10, "slug": "health"},
        {"name": "Transport", "amount": "₹25.00", "percent": 5, "slug": "transport"},
        {"name": "Entertainment", "amount": "₹15.99", "percent": 5, "slug": "entertainment"},
        {"name": "Other", "amount": "₹10.00", "percent": 5, "slug": "other"},
    ]
    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
