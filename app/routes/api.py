"""JSON API. Stateless (no cookies are read), so no CSRF token is needed."""
from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from app.services import PDFParseError, ResumeAnalyzer
from app.utils.validators import validate_upload

api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health():
    return jsonify(status="ok")


@api_bp.post("/analyze")
def analyze():
    file = request.files.get("resume")
    error = validate_upload(file, current_app.config["ALLOWED_EXTENSIONS"])
    if error:
        return jsonify(error=error), 400

    analyzer = ResumeAnalyzer.from_config(current_app.config)
    try:
        report = analyzer.analyze(
            file.stream,
            filename=secure_filename(file.filename) or "resume.pdf",
            job_description=request.form.get("job_description"),
        )
    except PDFParseError as exc:
        return jsonify(error=str(exc)), 422

    return jsonify(report.to_dict())
