# PharmaHive

PharmaHive is a secure Flask-based social web application designed for the pharmacy community, with a strong focus on backend architecture and security best practices.

---

## 🌐 Live Demo

https://pharmahive.xyz

**Deployment:** Hosted on Render with PostgreSQL (Supabase)

---

## 🚀 Features

* User authentication system (register, login, logout)
* Profile management (update username, email, and bio)
* Secure password change with current password verification
* Account deletion with password confirmation
* Password reset via OTP verification
* Reset session expiry for secure password recovery
* Public user profiles displaying:

  * Username, email, bio, and account creation date
  * Total number of posts
  * All posts created by the user
* Authorization checks to ensure users can only manage their own data
* Create, edit, and delete posts
* Global community feed displaying posts from all users
* Post like/unlike functionality
* Persistent like count for each post

---

## 🔐 Security Features

* Custom CSRF protection (implemented manually without external libraries)
* Secure session configuration:

  * HttpOnly cookies
  * SameSite=Lax
  * Secure cookies over HTTPS
* Strict Content Security Policy (CSP) to mitigate XSS
* Security headers:

  * X-Content-Type-Options (nosniff)
  * X-Frame-Options (DENY)
  * Referrer-Policy (strict-origin-when-cross-origin)
* Password hashing using Werkzeug
* Input validation and safe form handling
* Protection against open redirects
* Authorization logic to enforce user ownership of resources

---

## ✉️ Email Service

PharmaHive uses **Resend** for sending emails (OTP verification, password reset, etc.).

> ⚠️ Make sure your domain (e.g. `mail.pharmahive.xyz`) is verified in Resend before testing email features.

---

## 🛠️ Tech Stack

* Python
* Flask
* SQLAlchemy (ORM)
* PostgreSQL (Supabase)
* Flask-Migrate (Alembic)
* Jinja2
* Bootstrap
* Resend (Email service)

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
RESEND_API_KEY=your_resend_api_key
FLASK_ENV=development
```

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/abdelrahman-ayman2/PharmaHive.git
cd PharmaHive
```

---

### 2. Create a virtual environment

```bash
python -m venv venv
```

#### Activate it:

* **Windows:**

```bash
venv\Scripts\activate
```

* **Mac/Linux:**

```bash
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set up environment variables

Create a `.env` file as shown above.

---

### 5. Run database migrations

```bash
flask db upgrade
```

---

### 6. Run the application

```bash
python run.py
```

---

### 7. Open in browser

```
http://127.0.0.1:5000
```

---

## 🔮 Future Improvements

* Comments system for posts
* About page
* Admin panel with role-based access control
* Notification system
* Rate limiting for auth endpoints
* Guest browsing support
* Caching for performance
* REST API version (possibly FastAPI)
* UI/UX improvements for content readability
