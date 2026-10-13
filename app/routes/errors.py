"""Error handlers: JSON for /api/*, HTML pages everywhere else."""
import logging

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException, InternalServerError, RequestEntityTooLarge

log = logging.getLogger(__name__)


def _respond(code: int, title: str, message: str):
    if request.path.startswith("/api/"):
        return jsonify(error=message), code
    return render_template("error.html", code=code, title=title, message=message), code


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(RequestEntityTooLarge)
    def too_large(_exc):
        limit_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        return _respond(413, "File too large", f"Uploads are limited to {limit_mb} MB.")

    @app.errorhandler(HTTPException)
    def http_error(exc: HTTPException):
        return _respond(exc.code or 500, exc.name, exc.description or exc.name)

    @app.errorhandler(Exception)
    def unhandled(exc: Exception):
        log.exception("Unhandled error")
        return _respond(500, "Something went wrong", InternalServerError.description)
