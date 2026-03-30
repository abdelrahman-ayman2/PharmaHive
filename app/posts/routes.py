from flask import Blueprint, redirect, g, url_for, request, flash, render_template, abort
from urllib.parse import urlparse
from ..core.decorators import login_required
from ..core.helpers import valid_length, is_safe_url
from ..models.post import Post
from ..extensions import db
from sqlalchemy.exc import IntegrityError

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/create', methods=['POST'])
@login_required
def create():
    
    content = request.form.get("content", "").strip()
    if not content:
        flash("Post cannot be empty", "danger")
        return redirect(url_for("core.home"))
    
    is_valid, error = valid_length(content, 1, 280, "content")
    if not is_valid:
        flash(error, "danger")
        return redirect(url_for("core.home"))
    
    post = Post(
        content=content,
        user_id=g.user.id
    )
    try:
        db.session.add(post)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Something went wrong while creating the post.", "danger")
        return redirect(url_for("core.home"))
    
    flash("Post created successfully.", "success")
    return redirect(url_for("core.home"))

@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):

    post = Post.query.get_or_404(post_id)

    next_page = request.form.get("next_page")

    if not next_page or not is_safe_url(next_page):
        next_page = url_for("core.home")

    if g.user.id != post.user_id:
        abort(403)
        
    try:
        db.session.delete(post)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Something went wrong while deleting the post.", "danger")
        return redirect(next_page)
    
    flash("Post deleted successfully.", "success")
    return redirect(next_page)

@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if g.user.id != post.user_id:
        flash("You are not allowed to edit this post.", "danger")
        return redirect(url_for("core.home"))
    
    if request.method == 'POST':
        content = request.form.get("content", "").strip()
        referrer = request.form.get("next_page")

        next_page = urlparse(referrer).path if referrer else None

        if not next_page or not is_safe_url(next_page):
            next_page = url_for("core.home")

        if not content:
            flash("Post cannot be empty", "danger")
            return redirect(next_page)
        
        is_valid, error = valid_length(content, 1, 280, "Post")
        if not is_valid:
            flash(error, "danger")
            return redirect(next_page)

        try:
            post.content = content
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Something went wrong while editing the post.", "danger")
            return redirect(next_page)

        flash("Post edited successfully.", "success")
        return redirect(next_page)
    
    return render_template("posts/edit_post.html", post=post, user=g.user)

