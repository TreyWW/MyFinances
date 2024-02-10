import json
import mimetypes
import os
import sys
from pathlib import Path

import environ
from django.contrib.messages import constants as messages

env = environ.Env(DEBUG=(bool, False))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = True if os.environ.get("DEBUG") in ["True", "true", "TRUE", True] else False

env = environ.Env()
environ.Env.read_env()
DEBUG = True if os.environ.get("DEBUG") in ["True", "true", "TRUE", True] else False

try:
    if DEBUG:
        print("[BACKEND] Using local settings", flush=True)
        from .local_settings import *
    else:
        print("[BACKEND] Using production settings", flush=True)
        from .prod_settings import *
except ImportError:
    exit("[BACKEND] Couldn't import settings")

INSTALLED_APPS = [
    "django_extensions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "backend",
    "mathfilters",
    "django.contrib.humanize",
    "django_htmx",
    "debug_toolbar",
    "markdownify.apps.MarkdownifyConfig",
    "django_components",
    "django_components.safer_staticfiles",
    "social_django",
]

LOGIN_REQUIRED_IGNORE_VIEW_NAMES = [
    "index",
    "login",
    "login create_account",
    "login create_account manual",
    "login forgot_password",
    "user set password reset",
    "user set password",
    "user set password set",
    "logout",
    "invoices view invoice",
    "social:begin",
    "social:complete",
    "social:disconnect",
]

# @login_required()

LOGIN_REQUIRED_IGNORE_PATHS = [r"/login/$", "/accounts/github/login/callback/$"]
# for some reason only allows "login" and not "login create account" or anything

BASE_DIR = Path(__file__).resolve().parent.parent

EMAIL_WHITELIST = []
AUTHENTICATION_BACKENDS = [
    # "django.contrib.auth.backends.ModelBackend",
    "backend.auth_backends.EmailInsteadOfUsernameBackend",
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.google.GoogleOAuth2",
]

SECRET_KEY = os.environ.get("SECRET_KEY")

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard"

ROOT_URLCONF = "backend.urls"
SESSION_COOKIE_AGE = 604800
SESSION_ENGINE = "django.contrib.sessions.backends.db"
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATICFILES_DIRS = [
    BASE_DIR / "frontend/static",
]
mimetypes.add_type("text/javascript", ".js", True)

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-error",
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "frontend/templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "backend.context_processors.extras",
                "backend.context_processors.navbar",
                "backend.context_processors.breadcrumbs",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "django_components.template_loader.Loader",
                    ],
                )
            ],
            "builtins": [
                "django_components.templatetags.component_tags",
            ],
        },
    },
]

WSGI_APPLICATION = "settings.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "login_required.middleware.LoginRequiredMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "backend.models.CustomUserMiddleware",
]
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    "localhost",
    # ...
]
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp/cache/",  # Set the path to a directory for caching
    }
}

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": ["a", "p", "h1", "h2", "h3", "h4", "h5", "h6", "strong"],
        "WHITELIST_ATTRS": ["href", "src", "alt"],
    }
}

AUTH_USER_MODEL = "backend.User"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "GMT"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]
SOCIAL_AUTH_GITHUB_KEY = os.environ.get("GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get("GITHUB_SECRET")
SOCIAL_AUTH_GITHUB_ENABLED = (
    True if SOCIAL_AUTH_GITHUB_KEY and SOCIAL_AUTH_GITHUB_SECRET else False
)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = None
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = None
SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED = (
    True
    if SOCIAL_AUTH_GOOGLE_OAUTH2_KEY and SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
    else False
)

# SOCIAL_AUTH_LOGIN_URL = "/login/external/"
# SOCIAL_AUTH_NEW_USER_REDIRECT_URL = "/login/external/new_user/"
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_USER_MODEL = "backend.User"


AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_SIGNATURE_NAME = "s3v4"
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERITY = True
AWS_ENABLED = True if os.environ.get("AWS_ENABLED", "").lower() == "true" else False

AWS_TEXTRACT_ACCESS_KEY_ID = os.environ.get("AWS_TEXTRACT_ACCESS_KEY_ID")
AWS_TEXTRACT_REGION_NAME = os.environ.get("AWS_TEXTRACT_REGION_NAME") or "eu-west-2"
AWS_TEXTRACT_SECRET_ACCESS_KEY = os.environ.get("AWS_TEXTRACT_SECRET_ACCESS_KEY")
AWS_TEXTRACT_ENABLED = os.environ.get("AWS_TEXTRACT_ENABLED", "").lower() != "false"
AWS_TEXTRACT_ENABLED = (
    AWS_TEXTRACT_ENABLED
    and AWS_TEXTRACT_ACCESS_KEY_ID
    and AWS_TEXTRACT_SECRET_ACCESS_KEY
)

if (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) and AWS_ENABLED:
    print("[BACKEND] AWS S3 Media storage is enabled.")
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

SENDGRID_TEMPLATE = os.environ.get("SENDGRID_TEMPLATE")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_FROM_ADDRESS = os.environ.get("SENDGRID_FROM_ADDRESS")
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_API_KEY")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SERVER_ENABLED = True if EMAIL_HOST_PASSWORD else False

SENDGRID_SANDBOX_MODE_IN_DEBUG = True

if "test" in sys.argv[1:]:
    print("[BACKEND] Using sqlite3 database due to a test being ran", flush=True)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
    # check if the app is running from a manage.py test command, if so then use SQLITE with memory, faster than xampp
