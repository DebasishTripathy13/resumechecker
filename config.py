"""Application configuration classes."""
import os
import secrets


class Config:
    # Falls back to a per-process random key; set SECRET_KEY in production so
    # sessions survive restarts and work across multiple workers.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB upload cap (enforced by Flask)
    ALLOWED_EXTENSIONS = {"pdf"}
    MAX_PDF_PAGES = 10
    MAX_JOB_DESCRIPTION_CHARS = 20_000

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key"


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
