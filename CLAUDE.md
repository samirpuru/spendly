# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Spendly Expense Tracker

A multi-step educational expense tracker application built with Flask and SQLite. The app guides students through implementing user registration, authentication, profile pages, and expense management features. The codebase uses **no ORMs** — all database access is raw sqlite3 with parameterized queries.

## Development Commands

**Run the app**
```bash
python app.py
```
Starts Flask development server on http://localhost:5001. The app auto-initializes the SQLite database and seeds demo data on startup.

**Create a new feature spec and branch**
```
/create-spec <step_number> <feature_name>
```
Example: `/create-spec 5 add-expense`. This skill:
- Parses arguments into step number, feature title, and branch name
- Creates a feature branch (`feature/<slug>`)
- Generates a spec document at `.claude/specs/<step>-<slug>.md`
Review the spec, then use Shift+Tab (Plan Mode) to begin implementation.

**Seed test data**
```
/seed-user
```
Creates a single random Indian user with email and password "password123".

```
/seed-expense <user_id> <count> <months>
```
Generates realistic dummy expenses for a user. Example: `/seed-expense 1 50 6` creates 50 expenses spread across 6 months.

## Architecture

### Core Files

**`app.py`** — Main Flask application
- Route definitions (landing, register, login, logout, profile, and stubs for expense CRUD)
- `@login_required` decorator for protected routes
- Stateless session management (user_id, user_name stored in session)
- Placeholder routes return text strings; students implement real views

**`database/db.py`** — Data-access layer
- No ORM; all SQL is raw sqlite3 with parameterized queries
- `get_db()` — open a connection (enables row_factory, enforces foreign keys)
- `init_db()` — create users and expenses tables if not exist
- `seed_db()` — insert demo user and 8 sample expenses on first run
- `get_user_by_email(conn, email)` — lookup helper

**Database schema**
```
users (id, name, email, password_hash, created_at)
  - id: PRIMARY KEY AUTOINCREMENT
  - email: UNIQUE NOT NULL
  - password_hash: hashed with werkzeug.security.generate_password_hash

expenses (id, user_id, amount, category, date, description, created_at)
  - id: PRIMARY KEY AUTOINCREMENT
  - user_id: FOREIGN KEY → users.id
  - category: one of Food, Transport, Bills, Health, Entertainment, Shopping, Other
  - date: YYYY-MM-DD format
```

**`templates/`** — Jinja2 templates
- `base.html` — base layout; all templates extend this
- Static pages: `landing.html`, `register.html`, `login.html`, `terms.html`, `privacy.html`
- Dynamic pages: `profile.html` (Step 4, currently static with hardcoded data)
- Future: `add_expense.html`, `edit_expense.html`, `expense_detail.html`

**`static/`** — Assets
- `css/` — stylesheets; use CSS variables, never hardcode hex values
- `js/` — JavaScript (minimal; mostly form validation and interactions)

**`seed_*.py`** — Standalone seed scripts
- `seed_single_user.py` — creates a random Indian user (used by `/seed-user`)
- `seed_expense_script.py` — batch generates expenses (used by `/seed-expense`)

### Specs and Roadmap

Each feature is defined in `.claude/specs/<step>-<slug>.md`. Current status:
- ✅ Step 1: Database setup (schema, init, seed)
- ✅ Step 2: Registration (form validation, password hashing, email uniqueness)
- ✅ Step 3: Login and logout (session management, protected routes)
- ✅ Step 4: Profile page (static UI, hardcoded data; no real queries yet)
- ⏳ Step 5+: Wire up database queries, add/edit/delete expenses, export reports, etc.

## Conventions and Rules

**SQL and Database**
- No ORMs (SQLAlchemy, etc.) — only raw sqlite3
- All queries must be parameterized: `conn.execute("SELECT * FROM users WHERE id = ?", (id,))`
- No string formatting in SQL: never `f"SELECT * FROM users WHERE id = {id}"`
- Foreign key enforcement must be enabled: `conn.execute("PRAGMA foreign_keys = ON")`
- Always close database connections in `finally` blocks or use context managers

**Password Security**
- Hash passwords with `werkzeug.security.generate_password_hash()`
- Verify with `werkzeug.security.check_password_hash(hashed, plain)`
- Never log or expose password hashes

**Frontend**
- All templates extend `base.html`
- Use CSS variables for colors — define in `static/css/` and reference in templates
- No inline styles in HTML; no hardcoded hex values
- No tailwind — use semantic HTML and vanilla CSS
- Form validation: client-side (for UX) and server-side (for security)

**Authentication**
- Sessions store only `user_id` and `user_name` (minimal, stateless)
- Protected routes use `@login_required` decorator; unauthenticated requests redirect to `/login`
- Check `session.get("user_id")` before accessing user-specific data

**Commits and Branches**
- Feature branches: `feature/<slug>` (created by `/create-spec`)
- Commit messages: concise, imperative ("add expense form", not "added")
- Merge to `master` only after code review and passing tests (use PR workflow)
- Use `/code-review` skill before submitting PRs

## Custom Skills

**Project-specific skills** (available via `/skill-name`):
- `/create-spec` — spin up a new feature (creates branch and spec file)
- `/seed-user` — create a random test user
- `/seed-expense` — generate dummy expenses for testing

**General skills** (useful during development):
- `/code-review` — review current diff for bugs and simplifications
- `/verify` — test changes end-to-end by running the app
- `/run` — start the app and verify a feature works

## Testing

No automated test suite yet; feature validation is manual.
To test a feature:
1. Run `python app.py` to start the server
2. Open http://localhost:5001 in a browser
3. Exercise the feature flow (e.g., register → login → view profile)
4. Use `/verify` skill to confirm the feature works as spec'd

## Common Development Tasks

**Add a new route**
1. Define the function in `app.py` with `@app.route()`
2. If protected, add `@login_required` decorator
3. Create or modify a template in `templates/`
4. Use parameterized queries via `get_db()` for any data access
5. Test by visiting the URL in the browser

**Query the database**
```python
conn = get_db()
try:
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    # Access columns: user["id"], user["email"], etc.
finally:
    conn.close()
```

**Modify a template**
1. Edit the `.html` file in `templates/`
2. Ensure it extends `base.html` (unless it's a standalone fragment)
3. Use CSS variables from `static/css/`; no inline styles
4. Test by reloading the browser (Flask auto-reloads on save)

**Add dummy data**
```bash
/seed-user                    # Add one random user
/seed-expense 1 50 6          # Add 50 expenses to user ID 1 over 6 months
```

## Environment

- **Python version:** 3.8+ (tested with Flask 3.1.3)
- **Dependencies:** Flask, Werkzeug, Pytest (see `requirements.txt`)
- **Database:** SQLite (file: `expense_tracker.db`)
- **Port:** 5001 (configurable in `app.py`)
- **Secret key:** Set via `SECRET_KEY` env var; defaults to "dev-secret-key-change-in-production"

## Key Decisions

**No ORM** — Reinforces SQL fundamentals and gives students control over query performance. Using raw sqlite3 is safer (more transparent) than ORM abstractions for educational code.

**Hardcoded data in early steps** — Steps 2–4 use static/hardcoded data to validate the UI and routes without database complexity. Real queries are wired up later (Step 5+).

**Session-based auth (not JWT)** — Simple, session-per-user model is clearer for learning. JWT added in a later refactor if needed.

**No static asset pipeline** — CSS and JS are vanilla files in `static/`. No webpack, no PostCSS. Keeps the project lean and approachable.

## Troubleshooting

**Database locked or corrupted**
- Delete `expense_tracker.db` and restart the app; it will reinit and reseed

**Session lost after restart**
- Normal behavior; Flask dev server doesn't persist sessions across restarts. Log back in.

**CSS not updating**
- Flask caches static assets; clear browser cache (Ctrl+Shift+Delete) or do a hard refresh (Ctrl+F5)

**Port 5001 already in use**
- Modify `app.run(port=...)` in `app.py` or kill the process holding the port
