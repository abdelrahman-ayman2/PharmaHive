from flask import Blueprint, render_template, session
from ..core.decorators import login_required
from ..models.user import User
from ..extensions import db

users_bp = Blueprint('users', __name__, url_prefix='/u')

@users_bp.route('/<username>')
def profile(username):
    
    owner = User.query.filter_by(username=username).first_or_404()

    user_id = session.get("user_id")
                           
    if user_id:
        user = db.session.get(User, user_id)
    else:
        user = None
        
    return render_template("users/profile.html", user=user, owner=owner)