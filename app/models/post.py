from datetime import datetime
from sqlalchemy import text
from app.extensions import db

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    content = db.Column(db.Text, nullable=False)

    likes_count = db.Column(db.Integer, server_default=text("0"), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", back_populates="posts")