#pyhton
from flask import Blueprint, redirect, render_template, request, session, url_for, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
import re
from sqlalchemy.exc import IntegrityError
#myfunctions
from ..core.decorators import login_required, no_cache
from ..extensions import db, limiter
from ..models.user import User
from ..core.helpers import valid_length

account_bp = Blueprint('account', __name__, url_prefix='/account')

@account_bp.route("/")
@login_required
@no_cache
def account():
    user = g.user
    return render_template("account/account.html", user=user)

@account_bp.route("/edit", methods=['GET', 'POST'])
@limiter.limit("10 per hour", methods=["POST"])
@login_required
@no_cache
def edit_profile():
    user = g.user

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        bio = request.form.get('bio', '').strip()

        form_data={
                    "username": username,
                    "email": email,
                    "bio": bio
                }

        if not username or not email:
            flash("All fields are required", "danger")
            return render_template("account/edit_profile.html", user=user, form_data=form_data)
        
        elif username != user.username or email != user.email or bio != user.bio:

            is_valid, error = valid_length(username, 3, 64, "Username")
            if not is_valid:
                flash(error, "danger")
                return render_template("account/edit_profile.html", user=user, form_data=form_data)
            
            is_valid, error = valid_length(email, 8, 254, "Email")
            if not is_valid:
                flash(error, "danger")
                return render_template("account/edit_profile.html", user=user, form_data=form_data)
            
            is_valid, error = valid_length(bio, 0, 280, "Bio")
            if not is_valid:
                flash(error, "danger")
                return render_template("account/edit_profile.html", user=user, form_data=form_data)
            
            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

            if not re.fullmatch(email_pattern, email):
                flash("Invalid email format", "danger")
                return render_template("account/edit_profile.html", user=user, form_data=form_data)
            
            user.username = username
            user.email = email
            user.bio = bio

            try:
                db.session.commit()
                flash("Profile edited successfully", "success")
                return redirect(url_for("account.account"))
            except IntegrityError:
                db.session.rollback()
                flash("Username or email already exists", "danger")
                return render_template("account/edit_profile.html", user=user, form_data=form_data)
            
        else:
            flash("Nothing was edited", "warning")
            return render_template("account/edit_profile.html", user=user)
    
    return render_template("account/edit_profile.html", user=user, form_data=None)

@account_bp.route("/change-password", methods=['GET', 'POST'])
@limiter.limit("5 per 30 minutes", methods=["POST"])
@login_required
@no_cache
def change_password():
    if request.method == 'POST':

        password = request.form.get('password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password or not new_password or not confirm_password:
            flash("All fields are required", "danger")
            return redirect(url_for("account.change_password"))

        is_valid, error = valid_length(new_password, 8, 128, "New password")
        if not is_valid:
            flash(error, "danger")
            return redirect(url_for("account.change_password"))
        
        if new_password != confirm_password:
            flash("password doesn't match", "danger")
            return redirect(url_for("account.change_password"))
        
        pattern = r"^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).+$"

        if not re.fullmatch(pattern, new_password):
            flash("Password must be at least 8 characters, contain one uppercase letter and one special character.", "danger")
            return redirect(url_for("account.change_password"))
        
        user = g.user

        if check_password_hash(user.password_hash, password):
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash("Password changed successfully", "success")
            return redirect(url_for("account.account"))
        else:
            flash("Current password is incorrect", "danger")
            return redirect(url_for("account.change_password"))
        
    return render_template("account/change_password.html")

@account_bp.route("/delete", methods=['POST'])
@limiter.limit("2 per hour", methods=["POST"])
@login_required
def delete_account():
    password = request.form.get('password', '')
    if not password:
        flash("Password is required", "danger")
        return redirect(url_for("account.account"))

    user = g.user

    if check_password_hash(user.password_hash, password):
        try:
            db.session.delete(user)
            db.session.commit()

            session.clear()
            flash("Account deleted successfully", "success")
            return redirect(url_for("auth.login"))
        
        except Exception:
            db.session.rollback()
            flash("Something went wrong while deleting the account.", "danger")
            return redirect(url_for("account.account"))
    else:
        flash("Incorrect password", "danger")
        return redirect(url_for("account.account"))