# Spec: Edit Expense

## Overview

This feature allows logged-in users to modify an existing expense by changing its amount, category, date, and description. The edit form pre-populates with the current expense data, validates input on both client and server side, and persists changes to the database. This is a core expense management feature that empowers users to correct or update transaction details.

## Depends on

- Step 1: Database setup (expenses table schema)
- Step 3: Login and logout (session management and @login_required decorator)
- Step 4: Profile page (to see if expenses can be displayed from the database)

Note: This step assumes expenses exist in the database (either seeded or created via a future Add Expense feature). For testing, use `/seed-expense <user_id> <count> <months>` to generate test data.

## Routes

- `GET /expenses/<int:id>/edit` — Display the edit expense form pre-populated with the expense's current data — logged-in users only
- `POST /expenses/<int:id>/edit` — Save the edited expense and redirect to profile — logged-in users only

## Database changes

No new tables or columns needed. Uses the existing `expenses` table schema:
```
expenses (id, user_id, amount, category, date, description, created_at)
```

Verify the schema in `database/db.py` before implementation.

## Templates

- **Create:** `templates/edit_expense.html` — form for editing an expense with fields for amount, category, date, and description
- **Modify:** `templates/base.html` (no changes expected, but verify that edit_expense.html extends it)

## Files to change

- `app.py` — implement the `edit_expense(id)` route with GET and POST handlers
- `database/db.py` — add a helper function `get_expense_by_id(conn, expense_id, user_id)` to fetch a single expense (must verify ownership)

## Files to create

- `templates/edit_expense.html` — the form template

## New dependencies

No new dependencies. Uses existing Flask, sqlite3, and Werkzeug.

## Rules for implementation

- No SQLAlchemy or other ORMs; only raw sqlite3 with parameterized queries
- All queries must use parameterized placeholders: `?` syntax
- Never use string formatting in SQL queries
- Enable foreign key enforcement: `conn.execute("PRAGMA foreign_keys = ON")`
- Always close database connections in `finally` blocks
- Passwords are not involved in this feature; no security concern there
- Use CSS variables from `static/css/` — never hardcode hex values
- All templates must extend `base.html`
- Validate on server side (amount > 0, valid category, valid date format) even if client validates
- On POST, verify that the expense belongs to the logged-in user before updating
- On error, re-render the form with the validation error message and user input preserved
- On success, redirect to `/profile` to show the updated expense list

## Definition of done

- [ ] `GET /expenses/<int:id>/edit` displays a pre-filled form for an expense owned by the logged-in user
- [ ] Form includes fields: amount (decimal), category (dropdown with all 7 categories), date (YYYY-MM-DD), description (text)
- [ ] Submitting the form with valid data updates the expense in the database and redirects to `/profile`
- [ ] Form re-renders with an error message if any field is invalid (amount ≤ 0, invalid category, invalid date, etc.)
- [ ] Accessing an expense that doesn't exist or doesn't belong to the user returns a 404 or redirects to `/profile`
- [ ] CSS is styled consistently with the rest of the app (uses CSS variables, extends base.html)
- [ ] No SQL injection vulnerability; all queries use parameterized statements
- [ ] Test by running `/seed-user` and `/seed-expense 1 5 1` to create a test user and expenses, then navigate to `/expenses/1/edit` to edit an expense
