#python
from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from werkzeug.security import generate_password_hash
import re
from secrets import token_hex
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
#my functions
from .services import authenticate_user
from ..core.decorators import login_required, no_cache
from ..extensions import limiter
from ..extensions import db
from ..models.user import User
from ..models.otp import Otp
from ..core.helpers import valid_length, send_otp_email, is_valid_otp

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/')
def auth_index():
    return redirect(url_for('auth.login'))

#login
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per 10 minutes", methods=["POST"])
@no_cache
def login():
    if session.get("user_id"):
        return redirect(url_for("core.home"))
    
    if request.method == 'POST':
        email = request.form.get("email", '').strip().lower()
        password = request.form.get("password", '')

        result = authenticate_user(email, password)

        if not result.success:
            flash(result.message, "danger")
            return render_template("auth/login.html", form_data={"email": email})
        
        session.clear()
        session["user_id"] = result.user.id
        session["csrf_token"] = token_hex(32)

        flash(result.message, "success")
        return redirect(url_for("core.home"))

    return render_template('auth/login.html')

#register
@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour", methods=["POST"])
@no_cache
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
@limiter.limit("3 per 15 minutes", methods=["POST"])
@no_cache
def forgot_password():
    if request.method == 'POST':
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        try:
            if user is not None:
                otp = send_otp_email(email)
                session["otp_email"] = email

                Otp.query.filter_by(user_id=user.id).delete()

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
@limiter.limit("5 per 10 minutes", methods=["POST"])
@no_cache
def verify_otp():
    if request.method == 'POST':
        input_otp = request.form.get("otp")

        if not input_otp:
            flash("Please enter the verification code.", "danger")
            return render_template("auth/verify_otp.html")

        email = session.get("otp_email")
            
        if not email:
            flash("Invalid or expired code", "danger")
            return render_template("auth/verify_otp.html")
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Invalid or expired code", "danger")
            return render_template("auth/verify_otp.html")

        db_otp = Otp.query.filter_by(user_id=user.id).first()
            
        if not is_valid_otp(db_otp):
            flash("Invalid or expired code", "danger")
            return render_template("auth/verify_otp.html")
        
        if db_otp.otp != input_otp:
            flash("Invalid or expired code", "danger")
            return render_template("auth/verify_otp.html")
        
        try:
            db.session.delete(db_otp)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("VERIFY ERROR:", repr(e))
            flash("Something went wrong. Please try again.", "danger")
            return render_template("auth/verify_otp.html"), 500
        
        session["reset_user_id"] = user.id
        session["reset_allowed"] = True
        session["reset_expires_at"] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

        session.pop("otp_email", None)

        flash("Code verified successfully.", "success")
        return redirect(url_for("auth.reset_password"))
    
    return render_template('auth/verify_otp.html')

@auth_bp.route("/reset-password", methods=['POST', 'GET'])
@limiter.limit("3 per 15 minutes", methods=["POST"])
@no_cache
def reset_password():
    if not session.get("reset_allowed") or not session.get("reset_user_id") or not session.get("reset_expires_at"):
        flash("Invalid or expired reset session.", "danger")
        return redirect(url_for("auth.forgot_password"))
    
    expires_at = datetime.fromisoformat(session.get("reset_expires_at"))
    if datetime.utcnow() > expires_at:
        session.pop("reset_allowed", None)
        session.pop("reset_expires_at", None)
        session.pop("reset_user_id", None)

        flash("Invalid or expired reset session.", "danger")
        return redirect(url_for("auth.forgot_password"))
    
    if request.method == "POST":
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([password, confirm_password]):
            flash("All fields are required", "danger")
            return render_template('auth/reset_password.html')
        
        is_valid, error = valid_length(password, 8, 128, "Password")
        if not is_valid:
            flash(error, "danger")
            return render_template('auth/reset_password.html')
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template('auth/reset_password.html')
        
        pattern = r"^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).+$"

        if not re.fullmatch(pattern, password):
            flash("Password must be at least 8 characters, contain one uppercase letter and one special character.", "danger")
            return render_template('auth/reset_password.html')

        user = User.query.get(session.get("reset_user_id"))
        if not user:
            flash("Invalid or expired reset session.", "danger")
            return redirect(url_for("auth.forgot_password"))
        
        password_hash = generate_password_hash(password)
        user.password_hash = password_hash

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("RESET PASSWORD ERROR:", repr(e))
            flash("Something went wrong. Please try again.", "danger")
            return render_template("auth/reset_password.html"), 500
        
        session.pop("reset_allowed", None)
        session.pop("reset_expires_at", None)
        session.pop("reset_user_id", None)

        flash("Password changed successfully", "success")
        return redirect(url_for("auth.login"))

    return render_template('auth/reset_password.html')