import environ
import os
from pathlib import Path

DEBUG = True
env = environ.Env()
environ.Env.read_env()

CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1"]
BASE_DIR = Path(__file__).resolve().parent.parent

DB_TYPE = os.environ.get("DATABASE_TYPE")
DB_TYPE = DB_TYPE.lower() if DB_TYPE else "sqlite3"

DB_TYPE = "mysql" if DB_TYPE in ["mysql", "mariadb"] else DB_TYPE

if DB_TYPE == "mysql" or DB_TYPE == "postgres":
    DATABASES: dict = {
        "default": {
            "ENGINE": ("django.db.backends.postgresql_psycopg2" if DB_TYPE == "mysql" else "django.db.backends.postgresql"),
            "NAME": os.environ.get("DATABASE_NAME") or "myfinances_development",
            "USER": os.environ.get("DATABASE_USER") or "root",
            "PASSWORD": os.environ.get("DATABASE_PASS") or "",
            "HOST": os.environ.get("DATABASE_HOST") or "localhost",
            "PORT": os.environ.get("DATABASE_PORT") or (3306 if DB_TYPE == "mysql" else 5432),
            "OPTIONS": (
                {
                    "sql_mode": "traditional",
                }
                if DB_TYPE == "mysql"
                else {}
            ),
        }
    }

    print(f"[BACKEND] Using {DB_TYPE} database: {os.environ.get('DATABASE_NAME')}")

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    print("[BACKEND] Using sqlite3 database", flush=True)

ALLOWED_HOSTS: list[str | None] = ["localhost", "127.0.0.1"]

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # THIS WILL ALLOW HTTP - NOT RECOMMENDED
