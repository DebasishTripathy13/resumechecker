"""CSRF protection for HTML forms and baseline security headers."""
import hmac
import secrets

from flask import Response, session

_CSRF_KEY = "_csrf_token"


def generate_csrf_token() -> str:
    if _CSRF_KEY not in session:
        session[_CSRF_KEY] = secrets.token_urlsafe(32)
    return session[_CSRF_KEY]


def validate_csrf(token: str | None) -> bool:
    expected = session.get(_CSRF_KEY)
    return bool(expected and token and hmac.compare_digest(expected, token))


def apply_security_headers(response: Response) -> Response:
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data:; object-src 'none'; "
        "base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
    )
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    return response
