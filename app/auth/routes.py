#python
from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
import re
from sqlalchemy.exc import IntegrityError
#my functions
from ..core.decorators import login_required
from ..extensions import db
from ..models.user import User
from ..models.otp import Otp
from ..core.helpers import valid_length, send_otp_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/')
def auth_index():
    return redirect(url_for('auth.login'))

#login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("user_id"):
        return redirect(url_for("core.home"))
    
    if request.method == 'POST':
        email = request.form.get("email", '').strip().lower()
        password = request.form.get("password", '')

        if not all([email, password]):
            flash("All fields are required", "danger")
            return render_template("auth/login.html", form_data={"email": email})
        
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            flash("Logged in successfully.", "success")
            return redirect(url_for("core.home"))
        else:
            flash("Invalid email or password", "danger")
            return render_template("auth/login.html", form_data={"email": email})

    return render_template('auth/login.html')

#register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("user_id"):
        return redirect(url_for("core.home"))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        form_data={
                    "username" : username,
                    "email" : email,
                }

        if not all([username, email, password, confirm_password]):
            flash("All fields are required", "danger")
            return render_template('auth/register.html', form_data=form_data)
        
        is_valid, error = valid_length(username, 3, 64, "Username")
        if not is_valid:
            flash(error, "danger")
            return render_template('auth/register.html', form_data=form_data)
        
        is_valid, error = valid_length(email, 6, 254, "Email")
        if not is_valid:
            flash(error, "danger")
            return render_template('auth/register.html', form_data=form_data)
        
        is_valid, error = valid_length(password, 8, 128, "Password")
        if not is_valid:
            flash(error, "danger")
            return render_template('auth/register.html', form_data=form_data)
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template('auth/register.html', form_data=form_data)
        
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.fullmatch(email_pattern, email):
            flash("Invalid email format", "danger")
            return render_template('auth/register.html', form_data=form_data)
        
        pattern = r"^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).+$"

        if not re.fullmatch(pattern, password):
            flash("Password must be at least 8 characters, contain one uppercase letter and one special character.", "danger")
            return render_template('auth/register.html', form_data=form_data)
        
        password_hash = generate_password_hash(password)
        
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists", "danger")
            return render_template('auth/register.html', form_data=form_data)
        
        flash("Account created successfully", "success")
        return redirect(url_for("auth.login"))
    
    return render_template('auth/register.html', form_data=None)

#logout
@auth_bp.route("/logout", methods=['POST']) 
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route("/forgot-password", methods=['POST', 'GET']) 
def forgot_password():
    if request.method == 'POST':
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        try:
            if user is not None:
                otp = send_otp_email(email)
                session["otp_email"] = email

                new_otp = Otp(
                    otp=otp,
                    user_id=user.id
                )

                db.session.add(new_otp)
                db.session.commit()
        
            flash("If an account with that email exists, a verification code has been sent.", "info")
            return redirect(url_for("auth.verify_otp"))
        except Exception as e:
            db.session.rollback()
            print("FORGOT ERROR:", repr(e))
            flash("Something went wrong. Please try again.", "danger")
            return render_template("auth/forgot_password.html"), 500
        
    return render_template('auth/forgot_password.html')

@auth_bp.route("/verify-otp", methods=['POST', 'GET']) 
def verify_otp():
    return render_template('auth/verify_otp.html')

@auth_bp.route("/reset-password", methods=['POST', 'GET']) 
def reset_password():
    return render_template('auth/set_new_password.html')