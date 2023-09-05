import os, environ

DEBUG = True
env = environ.Env()
environ.Env.read_env()

CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1']

if os.environ.get('DATABASE_TYPE') in ["sqlite3", "sqlite", "SQLITE3", "SQLITE", "SQLite", "SQLite3"]:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get("DATABASE_NAME") or "myfinances_development",
            'USER': os.environ.get("DATABASE_USER") or "root",
            'PASSWORD': os.environ.get("DATABASE_PASS") or "",
            'HOST': os.environ.get("DATABASE_HOST") or "localhost",
            'PORT': os.environ.get("DATABASE_PORT") or 3306,
            'OPTIONS': {
                'sql_mode': 'traditional',
            }
        }
    }

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # THIS WILL ALLOW HTTP - NOT RECOMMENDED