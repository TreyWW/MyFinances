FROM python:3.12-slim AS base

ENV PYTHONBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        libffi-dev \
        curl \
        && rm -rf /var/lib/apt/lists/*

FROM base AS builder

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry==2.2.1

WORKDIR /MyFinances

COPY pyproject.toml poetry.lock ./
COPY package.json package-lock.json ./

ARG DATABASE_TYPE

RUN if [ "$DATABASE_TYPE" = "postgres" ]; then \
        poetry install --no-root --with postgres --without dev; \
    elif [ "$DATABASE_TYPE" = "mysql" ]; then \
        poetry install --no-root --with mysql --without dev; \
    else \
        poetry install --no-root --without dev; \
    fi

COPY ./frontend ./frontend
COPY ./assets ./assets
COPY webpack* .

RUN npm ci && npm run webpack-build

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
