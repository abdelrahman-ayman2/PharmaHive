from flask import Blueprint, redirect, render_template, g
from .decorators import login_required
from ..models.post import Post
from ..models.user import User
core_bp = Blueprint('core', __name__)


@core_bp.route('/')
@login_required
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    user = g.user
    return render_template('core/home.html', posts=posts, user=user)