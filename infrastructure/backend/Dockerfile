FROM python:3.12-slim AS base

ENV PYTHONBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        libffi-dev \
        curl \
        gcc \
        g++ \
        && rm -rf /var/lib/apt/lists/*

FROM base AS builder

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry==2.2.1

WORKDIR /MyFinances

ARG DATABASE_TYPE=sqlite

RUN if [ "$DATABASE_TYPE" = "mysql" ]; then \
        apt-get update && apt-get install -y default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*; \
    fi


COPY pyproject.toml poetry.lock ./
COPY package.json package-lock.json ./

RUN if [ "$DATABASE_TYPE" = "postgres" ]; then \
        poetry install --no-root --with postgres --without dev; \
    elif [ "$DATABASE_TYPE" = "mysql" ]; then \
        apt-get update && apt-get install -y \
         default-libmysqlclient-dev \
         libmariadb-dev-compat \
         libmariadb-dev \
         pkg-config \
      && rm -rf /var/lib/apt/lists/*; \
      poetry install --no-root --with mysql --without dev; \
    else \
        poetry install --no-root --without dev; \
    fi

RUN npm ci

COPY ./frontend ./frontend
COPY ./assets ./assets
COPY webpack* .

RUN npm run webpack-build

COPY . .

# needs all files as python is also used for tailwind vars
RUN npm run tailwind-minify

RUN chmod +x infrastructure/backend/scripts/*


FROM python:3.12-slim AS final

WORKDIR /MyFinances

# Copy only the app and installed Python packages from builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /MyFinances /MyFinances

ENTRYPOINT ["sh", "infrastructure/backend/scripts/entrypoint.sh"]
