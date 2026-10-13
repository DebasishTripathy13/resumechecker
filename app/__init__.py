"""Application factory."""
from flask import Flask

from config import config_by_name


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    from app.routes.api import api_bp
    from app.routes.errors import register_error_handlers
    from app.routes.main import main_bp
    from app.utils.security import apply_security_headers, generate_csrf_token

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    register_error_handlers(app)

    app.jinja_env.globals["csrf_token"] = generate_csrf_token
    app.after_request(apply_security_headers)

    return app
