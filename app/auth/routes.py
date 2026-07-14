#python
from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from secrets import token_hex
from datetime import datetime, timedelta
#my functions
from .services import authenticate_user, register_user, request_password_reset, verify_reset_otp, reset_user_password
from ..core.decorators import login_required, no_cache
from ..extensions import limiter

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
        session["user_id"] = result.data.id
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

        result = register_user(username, email, password, confirm_password)

        form_data={
                    "username" : username,
                    "email" : email,
                }
        
        if not result.success:
            flash(result.message, "danger")
            return render_template('auth/register.html', form_data=form_data)

        flash(result.message, "success")
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

        result = request_password_reset(email)

        if not result.success:
            flash(result.message, "danger")
            return render_template("auth/forgot_password.html"), 500
        
        flash(result.message, "info")
        session["otp_email"] = email
        return redirect(url_for("auth.verify_otp"))

    return render_template('auth/forgot_password.html')

@auth_bp.route("/verify-otp", methods=['POST', 'GET']) 
@limiter.limit("5 per 10 minutes", methods=["POST"])
@no_cache
def verify_otp():
    if request.method == 'POST':
        input_otp = request.form.get("otp")

        email = session.get("otp_email")

        result = verify_reset_otp(email, input_otp)

        if not result.success:
            flash(result.message, "danger")
            return render_template("auth/verify_otp.html")
        
        session["reset_user_id"] = result.data.id
        session["reset_allowed"] = True
        session["reset_expires_at"] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

        session.pop("otp_email", None)

        flash(result.message, "success")
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

        result = reset_user_password(session["reset_user_id"], password, confirm_password)

        if not result.success:
            flash(result.message, "danger")
            return render_template('auth/reset_password.html')
        
        session.pop("reset_allowed", None)
        session.pop("reset_expires_at", None)
        session.pop("reset_user_id", None)

        flash(result.message, "success")
        return redirect(url_for("auth.login"))

    return render_template('auth/reset_password.html')