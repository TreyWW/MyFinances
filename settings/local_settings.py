import os, environ
from pathlib import Path

DEBUG = True
env = environ.Env()
environ.Env.read_env()

CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1"]
BASE_DIR = Path(__file__).resolve().parent.parent

if os.environ.get("DATABASE_TYPE") in [
    "sqlite3",
    "sqlite",
    "SQLITE3",
    "SQLITE",
    "SQLite",
    "SQLite3",
]:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    print("[BACKEND] Using sqlite3 database", flush=True)
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DATABASE_NAME") or "myfinances_development",
            "USER": os.environ.get("DATABASE_USER") or "root",
            "PASSWORD": os.environ.get("DATABASE_PASS") or "",
            "HOST": os.environ.get("DATABASE_HOST") or "localhost",
            "PORT": os.environ.get("DATABASE_PORT") or 3306,
            "OPTIONS": {
                "sql_mode": "traditional",
            },
        }
    }
    print(f"[BACKEND] Using mysql database {os.environ.get('DATABASE_NAME')}")


ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

os.environ[
    "OAUTHLIB_INSECURE_TRANSPORT"
] = "1"  # THIS WILL ALLOW HTTP - NOT RECOMMENDED
