import sys
from pathlib import Path
import os, mimetypes, json, environ
from django.contrib.messages import constants as messages


env = environ.Env(DEBUG=(bool, False))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
print(f"test: {env('DEBUG')}")

DEBUG = True if os.environ.get("DEBUG") in ["True", "true", "TRUE", True] else False

env = environ.Env()
environ.Env.read_env()
DEBUG = True if os.environ.get("DEBUG") in ["True", "true", "TRUE", True] else False

try:
    if DEBUG:
        print("[BACKEND] Using local settings")
        from .local_settings import *
    else:
        print("[BACKEND] Using production settings")
        from .prod_settings.py import *
except ImportError:
    exit("[BACKEND] Couldn't import settings")

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django_extensions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "social_django",
    "backend",
    "mathfilters",
    "django.contrib.humanize",
    "django_htmx",
    "debug_toolbar",
    "markdownify.apps.MarkdownifyConfig",
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
]

# @login_required()

LOGIN_REQUIRED_IGNORE_PATHS = [r"/login/$"]
# for some reason only allows "login" and not "login create account" or anything

BASE_DIR = Path(__file__).resolve().parent.parent

EMAIL_WHITELIST = []
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
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
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATICFILES_DIRS = [
    BASE_DIR / "frontend/static",
]
mimetypes.add_type("text/javascript", ".js", True)

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

MESSAGE_TAGS = {
    messages.DEBUG: "border-blue-300 bg-blue-50 text-blue-800 dark:border-blue-800 dark:text-blue-400",
    messages.INFO: "border-blue-300 bg-red-50 text-blue-800 dark:border-blue-800 dark:text-blue-400",
    messages.SUCCESS: "border-green-300 bg-green-50 text-green-800 dark:border-green-800 dark:text-green-400",
    messages.WARNING: "border-yellow-300 bg-yellow-50 text-yellow-800 dark:border-yellow-800 dark:text-yellow-400",
    messages.ERROR: "border-red-300 bg-red-50 text-red-800 dark:border-red-800 dark:text-red-400",
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "frontend/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "backend.context_processors.notifications",
                "backend.context_processors.extras",
                "backend.context_processors.navbar",
                "backend.context_processors.toasts",
                "backend.context_processors.breadcrumbs",
                "social_django.context_processors.backends",
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
]
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    "localhost"
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


GOOGLE_OAUTH2_CLIENT_DETAILS = {
    "web": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": os.environ.get("GOOGLE_CLIENT_URI"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "scopes": ["openid", "email", "profile"],
    }
}

MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": ["a", "p", "h1", "h2", "h3", "h4", "h5", "h6", "strong"],
        "WHITELIST_ATTRS": ["href", "src", "alt"],
    }
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "GMT"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]
SOCIAL_AUTH_GITHUB_KEY = os.environ.get("GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get("GITHUB_SECRET")

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("GOOGLE_CLIENT_IDY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_SIGNATURE_NAME = "s3v4"
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERITY = True
AWS_ENABLED = (
    True if os.environ.get("AWS_ENABLED") in [True, "True", "true", "TRUE"] else False
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
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
    # check if the app is running from a manage.py test command, if so then use SQLITE with memory, faster than xampp
