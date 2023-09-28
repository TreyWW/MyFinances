import os, environ

env = environ.Env()
environ.Env.read_env()

DEBUG = False

CSRF_TRUSTED_ORIGINS = [f'https://{os.environ.get("URL")}', f'https://{os.environ.get("PROXY_IP")}']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("DATABASE_NAME"),
        'USER': os.environ.get("DATABASE_USER"),
        'PASSWORD': os.environ.get("DATABASE_PASS"),
        'HOST': os.environ.get("DATABASE_HOST"),
        'PORT': os.environ.get("DATABASE_PORT") or 3306,
        'OPTIONS': {
            'sql_mode': 'traditional',
        }
    }
}

ALLOWED_HOSTS = [os.environ.get("URL")]


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'  # THIS WILL ALLOW HTTP IF IT'S SET TO 1 - NOT RECOMMENDED