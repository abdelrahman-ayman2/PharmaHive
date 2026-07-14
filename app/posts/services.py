from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from ..core.helpers import valid_length
from ..models.post import Post
from ..models.like import Like
from ..extensions import db


class ServiceResult:
    def __init__(self, success, message=None, code=None, data=None):
        self.success = success
        self.message = message
        self.code = code
        self.data = data


def create_post(user_id, content):
    if not content:
        return ServiceResult(success=False, message="Post cannot be empty")

    is_valid, error = valid_length(content, 1, 280, "Content")
    if not is_valid:
        return ServiceResult(success=False, message=error)

    post = Post(content=content, user_id=user_id)
    try:
        db.session.add(post)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return ServiceResult(success=False, message="Something went wrong while creating the post.")

    return ServiceResult(success=True, message="Post created successfully.")


def delete_post(post_id, user_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return ServiceResult(success=False, code=404)

    if post.user_id != user_id:
        return ServiceResult(success=False, code=403)

    try:
        db.session.delete(post)
        db.session.commit()
        return ServiceResult(success=True, message="Post deleted successfully.")
    except Exception:
        db.session.rollback()
        return ServiceResult(success=False, message="Something went wrong while deleting the post.")


def get_post(post_id, user_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return ServiceResult(success=False, code=404)

    if post.user_id != user_id:
        return ServiceResult(success=False, code=403, message="You are not allowed to edit this post.")

    return ServiceResult(success=True, data=post)


def edit_post(post_id, user_id, content):
    post = db.session.get(Post, post_id)
    if post is None:
        return ServiceResult(success=False, code=404)

    if post.user_id != user_id:
        return ServiceResult(success=False, code=403, message="You are not allowed to edit this post.")

    if not content:
        return ServiceResult(success=False, message="Post cannot be empty")

    is_valid, error = valid_length(content, 1, 280, "Post")
    if not is_valid:
        return ServiceResult(success=False, message=error)

    try:
        post.content = content
        db.session.commit()
        return ServiceResult(success=True, message="Post edited successfully.")
    except Exception:
        db.session.rollback()
        return ServiceResult(success=False, message="Something went wrong while editing the post.")


def toggle_like(post_id, user_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return ServiceResult(success=False, code=404)

    existing_like = db.session.get(Like, (post_id, user_id))

    try:
        if existing_like is not None:
            db.session.delete(existing_like)
            db.session.execute(
                update(Post)
                .where(Post.id == post_id)
                .values(likes_count=Post.likes_count - 1)
            )
            liked = False
        else:
            db.session.add(Like(post_id=post_id, user_id=user_id))
            db.session.execute(
                update(Post)
                .where(Post.id == post_id)
                .values(likes_count=Post.likes_count + 1)
            )
            liked = True

        db.session.commit()
        db.session.refresh(post)
        return ServiceResult(success=True, data={"likes_count": post.likes_count, "liked": liked})
    except Exception as e:
        db.session.rollback()
        print("LIKE ERROR:", repr(e))
        return ServiceResult(success=False, message="Something went wrong")
