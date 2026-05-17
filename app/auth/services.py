from werkzeug.security import check_password_hash, generate_password_hash
from ..models.user import User

class LoginResult:
    def __init__(self, success, user=None, message=None):
        self.success = success
        self.user = user
        self.message = message

def authenticate_user(email, password):
    if not all([email, password]):
        return LoginResult(
            success=False,
            message="All fields are required"
        )
    
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return LoginResult(
            success=False,
            message="Invalid email or password"
        )
    
    return LoginResult(
        success=True,
        user=user,
        message="Logged in successfully."
    )
    

