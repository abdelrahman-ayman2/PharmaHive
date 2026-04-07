from datetime import datetime, timedelta
from app.extensions import db

class Otp(db.Model):
    __tablename__ = 'otp_codes'

    id = db.Column(db.Integer, primary_key=True)

    otp = db.Column(db.String(6), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=7), nullable=False, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)