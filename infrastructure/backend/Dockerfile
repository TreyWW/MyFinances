FROM python:3.12-alpine

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /MyFinances

COPY . .

#RUN #apk --no-cache --update add \
#    mariadb-connector-c-dev \
#    py-pip \
#    musl-dev \
#    gcc \
#    mariadb-dev \
#    libffi-dev


RUN apk add --no-cache --virtual .build-deps py-pip musl-dev gcc \
    && if [ "${DATABASE_TYPE}" = "mysql" ]; then \
        apk add --no-cache mariadb-dev \
        && poetry install --only mysql; \
    elif ["${TESTING}" != "true"] || ["${DATABASE_TYPE}" = "postgres"]; then \
        apk add --no-cache postgresql-dev \
        && poetry install --only postgres; \
    fi \
    && apk del .build-deps

RUN poetry install --without dev,mysql,postgres --no-root && rm -rf $POETRY_CACHE_DIR

RUN chmod +x infrastructure/backend/scripts/*
RUN chmod +x infrastructure/backend/scripts/tests/*
ENTRYPOINT ["sh", "infrastructure/backend/scripts/entrypoint.sh"]

EXPOSE 10012
EXPOSE 9012
