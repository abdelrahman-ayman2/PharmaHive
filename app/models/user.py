from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), nullable=False)

    email = db.Column(db.String(254), nullable=False)

    bio = db.Column(db.Text, nullable=False, default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    posts = db.relationship("Post", back_populates="user", cascade="all, delete-orphan", order_by="desc(Post.created_at)")

    __table_args__ = (
        db.Index("uq_users_username", "username", unique=True),
        db.Index("uq_users_email", "email", unique=True),
    )