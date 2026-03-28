from flask import url_for, session, redirect, g
from functools import wraps
from ..models.user import User
from ..extensions import db

def login_required(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("auth.login"))
        
        user = db.session.get(User, user_id)
        
        if user is None:
            session.clear()
            return redirect(url_for("auth.login"))
        
        g.user = user

        return f(*args, **kwargs)
    
    return decorator_function