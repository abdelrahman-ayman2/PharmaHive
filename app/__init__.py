#python 
from flask import Flask, abort
#my functions
from .config import Config
from .extensions import db, migrate
from .security.csrf import init_csrf
from .core.errors import error_handler
#blue print
from .auth.routes import auth_bp
from .account.routes import account_bp
from .core.routes import core_bp
from .users.routes import users_bp
from .posts.routes import posts_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY is not set")

    db.init_app(app)
    migrate.init_app(app, db)

    from .models import user, post
    
    with app.app_context():
        db.create_all()

    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)

    @app.after_request
    def security_headers(response):
        response.headers["Content-Security-Policy"] = app.config["CSP"]
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    error_handler(app)

    init_csrf(app)

    return app
    