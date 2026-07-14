from flask import Blueprint, redirect, g, url_for, request, flash, render_template, abort
from urllib.parse import urlparse
from ..core.decorators import login_required
from ..core.helpers import is_safe_url
from .services import create_post, delete_post, get_post, edit_post, toggle_like

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')


@posts_bp.route('/create', methods=['POST'])
@login_required
def create():
    content = request.form.get("content", "").strip()

    result = create_post(g.user.id, content)

    if not result.success:
        flash(result.message, "danger")
        return redirect(url_for("core.home"))

    flash(result.message, "success")
    return redirect(url_for("core.home"))


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    next_page = request.form.get("next_page")
    if not next_page or not is_safe_url(next_page):
        next_page = url_for("core.home")

    result = delete_post(post_id, g.user.id)

    if result.code == 404:
        abort(404)
    if result.code == 403:
        abort(403)

    if not result.success:
        flash(result.message, "danger")
        return redirect(next_page)

    flash(result.message, "success")
    return redirect(next_page)


@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    if request.method == 'POST':
        content = request.form.get("content", "").strip()
        referrer = request.form.get("next_page")
        next_page = urlparse(referrer).path if referrer else None
        if not next_page or not is_safe_url(next_page):
            next_page = url_for("core.home")

        result = edit_post(post_id, g.user.id, content)

        if result.code == 404:
            abort(404)
        if result.code == 403:
            flash(result.message, "danger")
            return redirect(url_for("core.home"))
        if not result.success:
            flash(result.message, "danger")
            return redirect(next_page)

        flash(result.message, "success")
        return redirect(next_page)

    result = get_post(post_id, g.user.id)

    if result.code == 404:
        abort(404)
    if result.code == 403:
        flash(result.message, "danger")
        return redirect(url_for("core.home"))

    return render_template("posts/edit_post.html", post=result.data, user=g.user)


@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def like(post_id):
    result = toggle_like(post_id, g.user.id)

    if result.code == 404:
        abort(404)
    if not result.success:
        return {"error": result.message}, 500

    return result.data
