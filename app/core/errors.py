from flask import render_template, redirect, session, url_for

def error_handler(app):

    @app.errorhandler(400)
    def bad_request(error):
        if session.get("user_id"):
            return redirect(url_for("core.home"))
        return render_template("errors/400.html"), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500
    
    @app.errorhandler(429)
    def too_many_requests(e):
        return render_template("errors/429.html"), 429