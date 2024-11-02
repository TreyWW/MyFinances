FROM --platform=$BUILDPLATFORM python:3.12-alpine

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /MyFinances

RUN apk add --no-cache --virtual .build-deps \
        musl-dev \
        gcc \
        g++ \
        libffi-dev \
        openssl-dev

COPY pyproject.toml poetry.lock ./

RUN if [ "${DATABASE_TYPE}" = "mysql" ]; then \
        apk add --no-cache mariadb-connector-c-dev && \
        poetry install --only mysql; \
    fi

RUN if [ "${TESTING}" != "true" ] || [ "${DATABASE_TYPE}" = "postgres" ]; then \
        apk add --no-cache postgresql-dev && \
        poetry install --only postgres; \
    fi

RUN apk del .build-deps

RUN poetry install --without dev,mysql,postgres --no-root && rm -rf $POETRY_CACHE_DIR

COPY . .

RUN chmod +x infrastructure/backend/scripts/*

ENTRYPOINT ["sh", "infrastructure/backend/scripts/entrypoint.sh"]

EXPOSE 10012
EXPOSE 9012
