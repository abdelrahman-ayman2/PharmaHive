# PharmaHive

PharmaHive is a secure Flask-based social web application designed for the pharmacy community, focusing on backend architecture and security best practices.

## Live Demo
https://pharmahive.xyz

**Deployment:** Hosted on Render with PostgreSQL database (Supabase)

---

## Features

- User authentication system (register, login, logout)
- Profile management (edit username, email, and bio)
- Secure password change with current password verification
- Account deletion with password confirmation
- Public user profiles displaying:
  - Username, email, bio, and account creation date
  - Total number of posts
  - All posts created by the user
- Authorization system to ensure users can only modify their own data
- Create and publish posts from the home page
- Global feed displaying posts from all users

---

## Security Features

- Custom CSRF protection implemented without external libraries
- Secure session management:
  - HttpOnly cookies
  - SameSite=Lax policy
  - Secure cookies over HTTPS
- Strict Content Security Policy (CSP) configuration to mitigate XSS attacks
- Security headers:
  - X-Content-Type-Options (nosniff)
  - X-Frame-Options (DENY)
  - Referrer-Policy (strict-origin-when-cross-origin)
- Password hashing using Werkzeug security utilities
- Input validation and form handling
- Authentication and authorization to ensure users can only access and modify their own data
- Protection against open redirects

---

## Tech Stack

- Python
- Flask
- SQLAlchemy (ORM)
- PostgreSQL (via Supabase)
- Flask-Migrate (database migrations)
- Jinja2 (templating)
- Bootstrap (UI)

---

## Environment Variables

Create a `.env` file in the project root and add the following variables:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
FLASK_ENV=development
```

---

## Run Locally

After setting up the `.env` file, run the following commands:

```bash
git clone https://github.com/abdelrahman-ayman2/PharmaHive.git
cd pharmahive

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python run.py

The application will run on http://127.0.0.1:5000
```