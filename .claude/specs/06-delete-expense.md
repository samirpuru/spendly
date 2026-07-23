# Spec: Delete Expense

## Overview

This feature allows logged-in users to permanently delete an existing expense. The delete operation is protected by ownership verification — a user can only delete their own expenses. A client-side confirmation dialog prevents accidental deletion, and the backend validates that the expense belongs to the user before removing it from the database. This is a critical expense management feature that gives users full control over their transaction history.

## Depends on

- Step 1: Database setup (expenses table schema)
- Step 3: Login and logout (session management and @login_required decorator)
- Step 4: Profile page (to see if expenses can be displayed from the database)
- Step 5: Edit expense (profile.html already includes the delete action link)

Note: This step assumes expenses exist in the database. For testing, use `/seed-user` and `/seed-expense <user_id> <count> <months>` to generate test data.

## Routes

- `POST /expenses/<int:id>/delete` — Delete an expense owned by the logged-in user and redirect to profile — logged-in users only

No new GET routes; the delete link in profile.html triggers a POST via JavaScript or form submission with client-side confirmation.

## Database changes

No new tables or columns needed. Uses the existing `expenses` table schema:
```
expenses (id, user_id, amount, category, date, description, created_at)
```

The DELETE operation will remove the row entirely.

## Templates

- **Create:** None (delete link already exists in profile.html from Step 5)
- **Modify:** None (profile.html already has the delete action link with `onclick="return confirm(...)"`)

If working in isolation before Step 5 is merged, you may need to add the delete action link to profile.html manually.

## Files to change

- `app.py` — implement the `delete_expense(id)` route with POST method that handles deletion
- `database/db.py` — add a helper function `delete_expense(conn, expense_id, user_id)` to safely delete a single expense

## Files to create

None.

## New dependencies

No new dependencies. Uses existing Flask, sqlite3, and Werkzeug.

## Rules for implementation

- No SQLAlchemy or other ORMs; only raw sqlite3 with parameterized queries
- All queries must use parameterized placeholders: `?` syntax
- Never use string formatting in SQL queries
- Enable foreign key enforcement: `conn.execute("PRAGMA foreign_keys = ON")`
- Always close database connections in `finally` blocks
- Verify that the expense belongs to the logged-in user before deleting (scoped WHERE clause)
- On successful delete, redirect to `/profile` to show the updated expense list
- On error (expense not found, doesn't belong to user), return a 404 or redirect to `/profile` with an error message
- Defense-in-depth: scoped delete by user_id in the WHERE clause prevents accidental modification of another user's data
- Use CSS variables from `static/css/` for any styling (though no new styles expected)
- All templates must extend `base.html`

## Definition of done

- [ ] `POST /expenses/<int:id>/delete` deletes an expense owned by the logged-in user and redirects to `/profile`
- [ ] Attempting to delete an expense that doesn't exist returns a 404 or redirects with an error
- [ ] Attempting to delete an expense belonging to another user returns a 404 or redirects (verified via user_id in WHERE clause)
- [ ] After deletion, the expense is no longer visible in the profile page transaction list
- [ ] The delete link in profile.html includes a client-side confirmation dialog (`onclick="return confirm('Delete this expense?')"`) to prevent accidental deletion
- [ ] No SQL injection vulnerability; all queries use parameterized statements
- [ ] Database connection is properly closed in a `finally` block
- [ ] Test by running `/seed-user` and `/seed-expense 1 5 1` to create test data, then delete an expense from the profile page and verify it's gone from the list
