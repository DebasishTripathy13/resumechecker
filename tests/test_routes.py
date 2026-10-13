import io


def _upload(data: bytes, name: str = "resume.pdf"):
    return (io.BytesIO(data), name)


def test_index_renders_with_csrf_and_csp(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'name="csrf_token"' in response.data
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_analyze_requires_csrf(client, strong_pdf):
    response = client.post("/analyze", data={"resume": _upload(strong_pdf)},
                           content_type="multipart/form-data")
    assert response.status_code == 400


def test_analyze_html_success(csrf_client, strong_pdf):
    response = csrf_client.post(
        "/analyze",
        data={"csrf_token": "test-token", "resume": _upload(strong_pdf),
              "job_description": "Python Kafka Kubernetes Terraform Snowflake"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Grade" in response.data
    assert b"snowflake" in response.data  # shown as a missing keyword


def test_analyze_rejects_non_pdf(csrf_client):
    response = csrf_client.post(
        "/analyze",
        data={"csrf_token": "test-token", "resume": _upload(b"hello", "resume.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"Only PDF files are supported" in response.data


def test_analyze_rejects_renamed_file(csrf_client):
    response = csrf_client.post(
        "/analyze",
        data={"csrf_token": "test-token", "resume": _upload(b"MZ\x90\x00 not a pdf")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"look like a valid PDF" in response.data


def test_api_analyze_returns_json(client, strong_pdf):
    response = client.post("/api/analyze", data={"resume": _upload(strong_pdf)},
                           content_type="multipart/form-data")
    assert response.status_code == 200
    body = response.get_json()
    assert 0 <= body["overall_score"] <= 100
    assert {c["key"] for c in body["checks"]} == {"contact", "sections", "content", "formatting", "keywords"}


def test_api_missing_file(client):
    response = client.post("/api/analyze", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_api_too_large(app, client):
    app.config["MAX_CONTENT_LENGTH"] = 1024
    response = client.post("/api/analyze", data={"resume": _upload(b"%PDF-" + b"0" * 4096)},
                           content_type="multipart/form-data")
    assert response.status_code == 413
    assert "limited" in response.get_json()["error"]


def test_404_page(client):
    response = client.get("/nope")
    assert response.status_code == 404
    assert b"Back to upload" in response.data


def test_health(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}
