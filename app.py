from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3
import os
from functools import wraps
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from database.db import (
    get_db, init_db, seed_db, get_user_by_email, get_user_by_id, get_expenses_by_user,
    get_expense_by_id, update_expense, delete_expense as delete_expense_row, CATEGORIES,
)

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
    conn = get_db()
    try:
        user_row = get_user_by_id(conn, session["user_id"])
        expenses = get_expenses_by_user(conn, session["user_id"])
    finally:
        conn.close()

    first_initial = user_row["name"][0].upper() if user_row["name"] else "U"
    last_initial = user_row["name"].split()[-1][0].upper() if len(user_row["name"].split()) > 1 else ""
    initials = first_initial + last_initial

    created_at = user_row["created_at"]
    created_date = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S") if created_at else datetime.now()
    member_since = created_date.strftime("%B %Y")

    user = {
        "name": user_row["name"],
        "email": user_row["email"],
        "initials": initials,
        "member_since": member_since,
    }

    transactions = []
    category_totals = {cat: 0.0 for cat in CATEGORIES}

    for expense in expenses:
        date_obj = datetime.strptime(expense["date"], "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d %b %Y")

        transactions.append({
            "id": expense["id"],
            "date": formatted_date,
            "description": expense["description"] or "No description",
            "category": expense["category"],
            "amount": f"₹{expense['amount']:.2f}",
            "amount_value": expense["amount"],
        })
        category_totals[expense["category"]] += expense["amount"]

    total_spent = sum(category_totals.values())
    transaction_count = len(expenses)
    top_category = max(category_totals, key=category_totals.get) if category_totals else "None"

    stats = {
        "total_spent": f"₹{total_spent:.2f}",
        "transaction_count": transaction_count,
        "top_category": top_category,
    }

    categories = []
    for cat in CATEGORIES:
        amount = category_totals[cat]
        if total_spent > 0:
            percent = int((amount / total_spent) * 100)
        else:
            percent = 0
        categories.append({
            "name": cat,
            "amount": f"₹{amount:.2f}",
            "percent": percent,
            "slug": cat.lower(),
        })

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


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    conn = get_db()
    try:
        expense = get_expense_by_id(conn, id, session["user_id"])
        if expense is None:
            abort(404)

        if request.method == "POST":
            amount_raw = request.form.get("amount", "").strip()
            category = request.form.get("category", "").strip()
            date_raw = request.form.get("date", "").strip()
            description = request.form.get("description", "").strip()

            error = None
            amount = None
            parsed_date = None

            try:
                amount = float(amount_raw)
            except (TypeError, ValueError):
                error = "Please enter a valid amount."

            if error is None and amount <= 0:
                error = "Amount must be greater than zero."

            if error is None and category not in CATEGORIES:
                error = "Please select a valid category."

            if error is None:
                try:
                    parsed_date = datetime.strptime(date_raw, "%Y-%m-%d")
                except ValueError:
                    error = "Please enter a valid date."

            if error is None:
                date_to_store = parsed_date.strftime("%Y-%m-%d")
                update_expense(
                    conn, id, session["user_id"],
                    amount, category, date_to_store, description or None,
                )
                conn.commit()
                return redirect(url_for("profile"))

            submitted = {
                "amount": amount_raw,
                "category": category,
                "date": date_raw,
                "description": description,
            }
            return render_template(
                "edit_expense.html",
                error=error, expense=submitted, categories=CATEGORIES, id=id,
            )

        return render_template(
            "edit_expense.html",
            expense=expense, categories=CATEGORIES, id=id,
        )
    finally:
        conn.close()


@app.route("/expenses/<int:id>/delete", methods=["POST"])
@login_required
def delete_expense(id):
    conn = get_db()
    try:
        rowcount = delete_expense_row(conn, id, session["user_id"])
        if rowcount == 0:
            abort(404)
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
