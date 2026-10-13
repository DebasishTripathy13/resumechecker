import io

import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app import create_app

STRONG_RESUME = [
    "Jane Doe",
    "jane.doe@example.com | +1 415 555 0134 | linkedin.com/in/janedoe | github.com/janedoe",
    "Summary",
    "Backend engineer with 6 years building scalable Python services on AWS.",
    "Experience",
    "Senior Software Engineer, Acme Corp (2021 - Present)",
    "- Led migration of 40 microservices to Kubernetes, cutting infra cost by 35%",
    "- Built a Kafka event pipeline processing 2 million events per day",
    "- Reduced API latency by 60% by optimizing PostgreSQL queries",
    "- Mentored 5 engineers and established code review standards",
    "- Designed CI/CD with GitHub Actions, shipping 3x more releases",
    "Software Engineer, Beta Inc (2018 - 2021)",
    "- Developed Flask REST APIs serving 500k users",
    "- Automated test suites with pytest, raising coverage to 90%",
    "- Implemented Redis caching that saved $20k per year",
    "- Launched a Docker-based dev environment adopted by 4 teams",
    "Projects",
    "- Created an open-source resume parser in Python with 1,200 GitHub stars",
    "Education",
    "B.S. Computer Science, State University, 2018",
    "Skills",
    "Python, Flask, Django, PostgreSQL, Redis, Kafka, Docker, Kubernetes, AWS, Terraform, Git, Linux",
    "Certifications",
    "AWS Certified Solutions Architect",
]

WEAK_RESUME = [
    "John Smith",
    "My resume",
    "I was responsible for various tasks at my job and I worked on stuff.",
]


def make_pdf(lines: list[str], pages: int = 1) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    for _ in range(pages):
        y = 750
        for line in lines:
            pdf.drawString(50, y, line)
            y -= 16
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()


@pytest.fixture
def app():
    return create_app("testing")


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def strong_pdf() -> bytes:
    return make_pdf(STRONG_RESUME)


@pytest.fixture
def weak_pdf() -> bytes:
    return make_pdf(WEAK_RESUME)


@pytest.fixture
def csrf_client(client):
    """A client whose session already holds a known CSRF token."""
    with client.session_transaction() as session:
        session["_csrf_token"] = "test-token"
    return client
