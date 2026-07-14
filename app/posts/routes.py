from flask import Blueprint, redirect, g, url_for, request, flash, render_template, abort
from urllib.parse import urlparse
from sqlalchemy import update
from ..core.decorators import login_required
from ..core.helpers import valid_length, is_safe_url
from ..models.post import Post
from ..models.like import Like
from ..extensions import db
from .services import create_post

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/create', methods=['POST'])
@login_required
def create():
    
    content = request.form.get("content", "").strip()

    result = create_post(g.user.id, content)

    if result.success == False:
        flash(result.message, "danger")
        return redirect(url_for("core.home"))

    flash(result.message, "success")
    return redirect(url_for("core.home"))

@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):

    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)

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
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
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

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def like(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404) 

    user = g.user
    existing_like = db.session.get(Like, (post.id, user.id))

    try:
        if existing_like is not None:
            db.session.delete(existing_like)
            db.session.execute(
                    update(Post)
                    .where(Post.id == post.id)
                    .values(likes_count=Post.likes_count - 1)
                )
            liked = False
        else:
            new_like = Like(post_id=post.id, user_id=user.id)
            db.session.add(new_like)
            db.session.execute(
                    update(Post)
                    .where(Post.id == post.id)
                    .values(likes_count=Post.likes_count + 1)
                )
            
            liked = True

        db.session.commit()
        db.session.refresh(post)
        
    except Exception as e:
        db.session.rollback()
        print("LIKE ERROR:", repr(e))
        return {"error": "Something went wrong"}, 500

    return {
        "likes_count": post.likes_count,
        "liked": liked
    }

