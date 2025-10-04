"""
Django settings for wordprjct project.
Modified for production deployment on Render.
"""

import os
from pathlib import Path
import environ

# ------------------------------------------------------------------------------
# BASE DIR
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# ------------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False)
)
# Load .env file if it exists (only useful in local dev)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ------------------------------------------------------------------------------
# SECURITY SETTINGS
# ------------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="unsafe-secret-key")  # set via ENV on Render
DEBUG = env("DEBUG")  # False on production

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

# ------------------------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps
    "game",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # for static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "wordprjct.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # you can place project-wide templates here
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wordprjct.wsgi.application"

# ------------------------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------------------------
# Uses DATABASE_URL if provided (Postgres on Render), otherwise SQLite locally
DATABASES = {
    "default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# ------------------------------------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"   # set to your region
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# STATIC FILES
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------------------------------------------------------------
# LOGIN / LOGOUT
# ------------------------------------------------------------------------------
LOGIN_REDIRECT_URL = "/admin-dashboard/"
LOGOUT_REDIRECT_URL = "/login/"

# ------------------------------------------------------------------------------
# SECURITY SETTINGS (Production only when DEBUG = False)
# ------------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ------------------------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
