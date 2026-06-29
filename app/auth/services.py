from werkzeug.security import check_password_hash, generate_password_hash
import re
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models.user import User
from ..models.otp import Otp
from ..core.helpers import valid_length, send_otp_email, is_valid_otp

class ServiceResult:
    def __init__(self, success, data=None, message=None):
        self.success = success
        self.data = data
        self.message = message

def authenticate_user(email, password):
    if not all([email, password]):
        return ServiceResult(
            success=False,
            message="All fields are required"
        )
    
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return ServiceResult(
            success=False,
            message="Invalid email or password"
        )
    
    return ServiceResult(
        success=True,
        data=user,
        message="Logged in successfully."
    )

def register_user(username, email, password, confirm_password):
    if not all([username, email, password, confirm_password]):
        return ServiceResult(
            success=False,
            message="All fields are required"
        )

    is_valid, error = valid_length(username, 3, 64, "Username")
    if not is_valid:
        return ServiceResult(
            success=False,
            message=error
        )
    
    is_valid, error = valid_length(email, 6, 254, "Email")
    if not is_valid:
        return ServiceResult(
            success=False,
            message=error
        )
            
    is_valid, error = valid_length(password, 8, 128, "Password")
    if not is_valid:
        return ServiceResult(
            success=False,
            message=error
        )

    if password != confirm_password:
        return ServiceResult(
            success=False,
            message="Passwords do not match"
        )

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.fullmatch(email_pattern, email):
        return ServiceResult(
            success=False,
            message="Invalid email format"
        )

    password_pattern = r"^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).+$"

    if not re.fullmatch(password_pattern, password):
        return ServiceResult(
            success=False,
            message="Password must be at least 8 characters, contain one uppercase letter and one special character."
        )

    password_hash = generate_password_hash(password)

    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return ServiceResult(
            success=False,
            message="Username or email already exists"
        )

    return ServiceResult(
        success=True,
        message="Account created successfully"
    )

def request_password_reset(email):
    user = User.query.filter_by(email=email).first()

    try:
        if user is not None:
            otp = send_otp_email(email)
    
            Otp.query.filter_by(user_id=user.id).delete()
    
            new_otp = Otp(
                otp=otp,
                user_id=user.id
            )
    
            db.session.add(new_otp)
            db.session.commit()
        
        return ServiceResult(
            success=True,
            message="If an account with that email exists, a verification code has been sent."
        )
    except Exception as e:
            db.session.rollback()
            print("FORGOT ERROR:", repr(e))

            return ServiceResult(
                success=False,
                message="Something went wrong. Please try again."
            )

def verify_reset_otp(email, input_otp):
    if not input_otp:
        return ServiceResult(
            success=False,
            message="Please enter the verification code."
        )

    if not email:
        return ServiceResult(
            success=False,
            message="Invalid or expired code"
        )

    user = User.query.filter_by(email=email).first()
    if not user:
        return ServiceResult(
            success=False,
            message="Invalid or expired code"
        )

    db_otp = Otp.query.filter_by(user_id=user.id).first()

    if not is_valid_otp(db_otp):
        return ServiceResult(
            success=False,
            message="Invalid or expired code"
        )

    if db_otp.otp != input_otp:
        return ServiceResult(
            success=False,
            message="Invalid or expired code"
        )

    try:
        db.session.delete(db_otp)
        db.session.commit()
        return ServiceResult(
            success=True,
            data=user,
            message="Code verified successfully."
        )
    except Exception as e:
        db.session.rollback()
        print("VERIFY ERROR:", repr(e))
        return ServiceResult(
            success=False,
            message="Something went wrong. Please try again."
        )