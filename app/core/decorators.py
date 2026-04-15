from flask import url_for, session, redirect, g, request, jsonify
from functools import wraps
from ..models.user import User
from ..extensions import db

def login_required(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id:
            return handle_unauthorized()
        
        user = db.session.get(User, user_id)
        
        if user is None:
            session.clear()
            return handle_unauthorized()
        
        g.user = user

        return f(*args, **kwargs)
    
    return decorator_function

def handle_unauthorized():
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"error": "unauthorized"}), 401

    # fallback (HTML)
    return redirect(url_for("auth.login"))