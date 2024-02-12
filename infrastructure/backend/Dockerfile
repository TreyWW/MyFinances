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


RUN if [ ${DATABASE_TYPE} = "mysql" ]; then \
        RUN apk add --no-cache --virtual .build-deps py-pip musl-dev gcc mariadb-dev && \
        RUN poetry install --only mysql \
    elif [ ${DATABASE_TYPE} = "postgres" ]; then \
        RUN apk add --no-cache --virtual .build-deps py-pip musl-dev gcc postgresql-dev && \
        RUN poetry install --only postgres \
    fi

RUN poetry install --without dev,mysql,postgres --no-root && rm -rf $POETRY_CACHE_DIR

RUN chmod +x infrastructure/backend/scripts/*
RUN chmod +x infrastructure/backend/scripts/tests/*
ENTRYPOINT ["sh", "infrastructure/backend/scripts/entrypoint.sh"]

EXPOSE 10012
EXPOSE 9012
