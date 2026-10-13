"""HTML pages: upload form and results."""
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app.services import PDFParseError, ResumeAnalyzer
from app.utils.security import validate_csrf
from app.utils.validators import validate_upload

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.post("/analyze")
def analyze():
    if not validate_csrf(request.form.get("csrf_token")):
        abort(400, description="Your session expired. Please refresh the page and try again.")

    file = request.files.get("resume")
    error = validate_upload(file, current_app.config["ALLOWED_EXTENSIONS"])
    if error:
        flash(error, "error")
        return redirect(url_for("main.index"))

    analyzer = ResumeAnalyzer.from_config(current_app.config)
    try:
        report = analyzer.analyze(
            file.stream,
            filename=secure_filename(file.filename) or "resume.pdf",
            job_description=request.form.get("job_description"),
        )
    except PDFParseError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index"))

    return render_template("result.html", report=report)
