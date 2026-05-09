from app.extensions import db

class Like(db.Model):
    __tablename__ = 'likes'

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, primary_key=True)

    post = db.relationship("Post", back_populates="likes")