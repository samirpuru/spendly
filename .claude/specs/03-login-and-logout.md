# Spec: Login and Logout

## Overview

Step 03 implements user authentication via login and session management via logout. Users can sign in with their email and password to access logged-in features, and sign out to clear their session. The system validates credentials against the database, uses Flask sessions to track authenticated users, and enforces access control on protected routes. This step depends on Step 02 (registration) and unlocks all subsequent logged-in features (profile, expense tracking).

## Depends on

- Step 01: Database Setup — users table with password_hash column must exist.
- Step 02: Registration — users must be able to create accounts before logging in.

## Routes

- `POST /login` — Submit login form (email + password) — access level: public
- `GET /login` — Render login form — access level: public (already exists)
- `POST /logout` — Clear session and redirect to home — access level: logged-in
- All currently-protected routes (profile, expenses) should redirect to `/login` if not authenticated

## Database changes

No database changes. The users table from Step 01 is used as-is.

## Templates

- **Modify:** `templates/login.html` — Ensure form has email and password fields, displays validation errors via `{% if error %}` block (structure already in place).
- **Modify:** `templates/base.html` — Update navbar to show different links based on login status (signed in: show name + logout link; signed out: show sign in + get started links).

## Files to change

- `app.py` — Implement POST `/login` handler, implement `/logout` handler, add session configuration, add login_required decorator or checks for protected routes.
- `templates/base.html` — Update navbar to render conditionally based on `session["user_id"]` (or similar session key).

## Files to create

No new files.

## New dependencies

No new dependencies. Flask's built-in `session` (already imported) is used for session management.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterized queries only
- Use werkzeug `check_password_hash` to verify passwords (do NOT store/compare plaintext)
- Use Flask's built-in `session` for user tracking (set `session["user_id"]` on successful login, clear on logout)
- Use `app.secret_key` to sign sessions (set a secret key in the app, e.g., a random string or env var)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Server-side validation only: email must be provided, password must be provided
- On login failure, re-render form with error message and preserve email field (clear password field)
- On logout, clear session and redirect to `/` or `/login`
- On login success, redirect to `/profile` or `/` (recommend `/profile` to match post-login user expectation)
- Protect `/profile` route: redirect unauthenticated users to `/login`

## Definition of done

- [ ] Login form displays correctly on GET /login
- [ ] Form has email and password fields, submit button
- [ ] User can successfully log in with valid email and password from a registered account
- [ ] Successful login redirects to `/profile` (or home, if /profile not yet fully built)
- [ ] Failed login re-renders form with error message, preserves email field, clears password field
- [ ] Invalid email → error "Please enter your email address." or "No account found with this email."
- [ ] Invalid password → error "Incorrect password." (do NOT reveal whether email exists, for security)
- [ ] Session is set on login: `session["user_id"]` contains the logged-in user's ID
- [ ] Session is cleared on logout: `/logout` clears session and redirects to `/` or `/login`
- [ ] Navbar reflects login status: signed-out users see "Sign in" + "Get started", signed-in users see account name/greeting + "Logout" link
- [ ] Unauthenticated access to `/profile` redirects to `/login` (or shows error page; redirect is preferred)
- [ ] Password comparison uses werkzeug `check_password_hash`, NOT plaintext comparison
- [ ] All error messages are user-friendly and do not leak account existence (except "no account" vs "wrong password" can be merged into one vague message for max security)
- [ ] No hardcoded colors in CSS or templates — only CSS variables
