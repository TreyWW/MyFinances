import os
from pathlib import Path

import environ

env = environ.Env()
environ.Env.read_env()

DEBUG = False

CSRF_TRUSTED_ORIGINS = [
    f'https://{os.environ.get("URL")}',
    f'https://{os.environ.get("PROXY_IP")}',
]
BASE_DIR = Path(__file__).resolve().parent.parent

DB_TYPE = os.environ.get("DATABASE_TYPE")
DB_TYPE = DB_TYPE.lower() if DB_TYPE else ""  # sqlite is disabled for production

DB_TYPE = "mysql" if DB_TYPE in ["mysql", "mariadb"] else DB_TYPE

DATABASES = {
    "default": {
        "ENGINE": (
            "django.db.backends.postgresql_psycopg2"
            if DB_TYPE == "mysql"
            else "django.db.backends.postgresql"
        ),
        "NAME": os.environ.get("DATABASE_NAME") or "myfinances_development",
        "USER": os.environ.get("DATABASE_USER") or "root",
        "PASSWORD": os.environ.get("DATABASE_PASS") or "",
        "HOST": os.environ.get("DATABASE_HOST") or "localhost",
        "PORT": os.environ.get("DATABASE_PORT")
        or (3306 if DB_TYPE == "mysql" else 5432),
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


ALLOWED_HOSTS = [os.environ.get("URL")]


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = (
    "0"  # THIS WILL ALLOW HTTP IF IT'S SET TO 1 - NOT RECOMMENDED
)
