from .base import *
from decouple import config

DEBUG = config("DEBUG", cast=bool, default=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="postgres"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="example"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage"  # or any media storage you'd like to use.
    },
    "staticfiles": {  # this is the storage for static files
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"  # this is django's default storage for static files, for using cloudinry as static files storage see usage with static files section
    },
}

CORS_ALLOWED_ORIGINS: list[str] = config(
    "CORS_ALLOWED_ORIGIN", "http://localhost:8000,http://127.0.0.1:8000"
).split(",")
