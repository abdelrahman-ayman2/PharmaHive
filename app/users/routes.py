from flask import Blueprint, render_template, abort
from ..core.decorators import login_required
from ..models.user import User

users_bp = Blueprint('users', __name__, url_prefix='/u')

@users_bp.route('/<username>')
@login_required
def profile(username):
    
    user = User.query.filter_by(username=username).first_or_404()
    
    return render_template("users/profile.html", user=user)