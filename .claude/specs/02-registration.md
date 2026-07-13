# Spec: Registration

## Overview

Step 02 implements user registration for Spendly. Users can create an account by providing their name, email, and password. The system validates input, enforces email uniqueness, hashes passwords securely, and saves new users to the database. On successful registration, users are redirected to the login page. This step builds on the database layer (Step 01) and is a prerequisite for authentication and all logged-in features.

## Depends on

- Step 01: Database Setup — users table must exist with proper schema and constraints.

## Routes

- `POST /register` — Submit registration form — access level: public
- `GET /register` — Render registration form — access level: public (already exists, template needs updating)

## Database changes

No database changes. The users table from Step 01 is used as-is.

## Templates

- **Modify:** `templates/register.html` — Add a registration form with fields for name, email, password, password confirmation, and submit button. Display validation errors if present.

## Files to change

- `app.py` — Implement POST handler for `/register` route (GET handler already exists)

## Files to create

No new files.

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterized queries only
- Passwords hashed with werkzeug `generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Client-side and server-side validation for:
  - Email format (basic check: contains @ and domain)
  - Password length (minimum 6 characters)
  - Password confirmation matches password
  - Name is not empty
- Email uniqueness enforced by database UNIQUE constraint and server-side error handling
- On validation error, re-render form with error message and preserve non-password fields
- On success, redirect to `/login` page
- Use HTTP 201 Created for successful registration responses is optional; 302 redirect is fine

## Definition of done

- [ ] Registration form displays correctly on GET /register
- [ ] Form has fields: name, email, password, password confirmation, submit button
- [ ] Form validation works: empty fields rejected, password mismatch caught
- [ ] User can successfully register with valid data
- [ ] Duplicate email rejected with clear error message
- [ ] Password is hashed before storage (not plain text in database)
- [ ] Successful registration redirects to login page
- [ ] Form preserves name and email on validation error (password fields cleared)
- [ ] No hardcoded colors in CSS — only CSS variables used
- [ ] All error messages are user-friendly and helpful
