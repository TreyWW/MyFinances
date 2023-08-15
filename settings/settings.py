from pathlib import Path
import os, mimetypes, json
from django.contrib.messages import constants as messages

import environ

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

INSTALLED_APPS = ['django.contrib.staticfiles',
                  'django_extensions',
                  'django.contrib.admin',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.messages',
                  'social_django',
                  'backend',
                  'mathfilters',
                  'django.contrib.humanize',
                  'django_htmx']

BASE_DIR = Path(__file__).resolve().parent.parent

EMAIL_WHITELIST = []
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
SECRET_KEY = os.environ.get("SECRET_KEY")
LOGIN_URL = '/login/'
ROOT_URLCONF = 'backend.urls'
SESSION_COOKIE_AGE = 1800
SESSION_ENGINE = "django.contrib.sessions.backends.db"
STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / "frontend/static", ]
mimetypes.add_type("text/javascript", ".js", True)


MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

MESSAGE_TAGS = {
    messages.DEBUG: 'border-blue-300 bg-blue-50 text-blue-800 dark:border-blue-800 dark:text-blue-400',
    messages.INFO: 'border-blue-300 bg-red-50 text-blue-800 dark:border-blue-800 dark:text-blue-400',
    messages.SUCCESS: 'border-green-300 bg-green-50 text-green-800 dark:border-green-800 dark:text-green-400',
    messages.WARNING: 'border-yellow-300 bg-yellow-50 text-yellow-800 dark:border-yellow-800 dark:text-yellow-400',
    messages.ERROR: 'border-red-300 bg-red-50 text-red-800 dark:border-red-800 dark:text-red-400',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend/templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'backend.context_processors.notifications',
                'backend.context_processors.extras',
                'backend.context_processors.navbar',
                'backend.context_processors.toasts'
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    # 'django_browser_reload.middleware.BrowserReloadMiddleware'
]
GOOGLE_OAUTH2_CLIENT_DETAILS = {
    'web': {
        'client_id': os.environ.get("GOOGLE_CLIENT_ID"),
        'client_secret': os.environ.get("GOOGLE_CLIENT_SECRET"),
        'redirect_uris': os.environ.get("GOOGLE_CLIENT_URI"),
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'scopes': [
            'openid',
            'email',
            'profile'

        ],
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'GMT'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SENDGRID_TEMPLATE = os.environ.get("SENDGRID_TEMPLATE")
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

SENDGRID_SANDBOX_MODE_IN_DEBUG = True