from flask import Blueprint, redirect, render_template, g, session
from .decorators import login_required
from ..models.post import Post
from ..models.user import User
from ..models.like import Like
from ..extensions import db
core_bp = Blueprint('core', __name__)


@core_bp.route('/')
def home():
    user_id = session.get("user_id")

    if user_id:
        user = db.session.get(User, user_id)
    else:
        user = None
    
    if user:
        likes = db.session.query(Like.post_id).filter_by(user_id=user.id).all()
        liked_post_ids = {post_id for (post_id,) in likes}
    else:
        liked_post_ids = set()

    posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template('core/home.html', posts=posts, user=user, liked_post_ids=liked_post_ids)