FROM python:3.12-alpine

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /MyFinances

# Install build dependencies including C++ compiler
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    mariadb-dev \
    postgresql-dev \
    curl

# Copy only dependency files first for better caching
COPY pyproject.toml poetry.lock ./

RUN if [ "${DATABASE_TYPE}" = "mysql" ]; then \
        poetry install --only mysql; \
    fi

# Install PostgreSQL dependencies if TESTING is not true or DATABASE_TYPE is postgres
RUN if [ "${TESTING}" != "true" ] || [ "${DATABASE_TYPE}" = "postgres" ]; then \
        poetry install --only postgres; \
    fi

RUN apk del .build-deps

RUN poetry install --without dev,mysql,postgres --no-root && rm -rf $POETRY_CACHE_DIR

COPY . .

RUN chmod +x infrastructure/backend/scripts/*

ENTRYPOINT ["sh", "infrastructure/backend/scripts/entrypoint.sh"]

EXPOSE 10012 9012
