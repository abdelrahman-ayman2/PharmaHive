from ..core.helpers import valid_length, is_safe_url
from ..models.post import Post
from ..extensions import db
from sqlalchemy.exc import IntegrityError


class ServiceResult:
    def __init__(self, success, message=None, code=None):
        self.success = success
        self.message = message
        self.code = code

def create_post(user_id, content):
    if not content:
        return ServiceResult(
            success=False,
            message="Post cannot be empty"
        )

    is_valid, error = valid_length(content, 1, 280, "Content")
    if not is_valid:
        return ServiceResult(
            success=False,
            message=error
        )

    post = Post(
        content=content,
        user_id=user_id
    )
    try:
        db.session.add(post)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return ServiceResult(
            success=False,
            message="Something went wrong while creating the post."
        )

    return ServiceResult(
        success=True,
        message="Post created successfully."
    )


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