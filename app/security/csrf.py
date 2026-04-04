from flask import session, request, abort
from secrets import token_hex

def generate_token():
    csrf_token = session.get("csrf_token")

    if not csrf_token:
        csrf_token = token_hex(32)
        session['csrf_token'] = csrf_token
        return csrf_token
    
    return session['csrf_token']

def init_csrf(app):
    @app.before_request
    def csrf_protect():
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            token = request.form.get('csrf_token', '') or request.headers.get("X-CSRFToken", "")
            session_token = session.get("csrf_token")

            if not token or not session_token or token != session_token:
                abort(400)

    @app.context_processor
    def inject_csrf_token():
        return dict(token=generate_token)

