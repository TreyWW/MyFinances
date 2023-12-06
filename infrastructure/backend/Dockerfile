# Dockerfile
FROM python:3.12-alpine

# Set the working directory
WORKDIR /MyFinances

COPY . .

RUN apk --no-cache --update add \
    mariadb-connector-c-dev \
    py-pip \
    musl-dev \
    gcc \
    mariadb-dev \
    git \
    libffi-dev 

RUN pip install --upgrade pip \
    && pip install mysql mariadb mysqlclient -r requirements.txt

CMD ["git","--version"]

# Set the entrypoint
#COPY ../scripts /infrastructure/scripts/
RUN chmod +x infrastructure/backend/scripts/*
RUN chmod +x infrastructure/backend/scripts/tests/*
ENTRYPOINT ["sh", "infrastructure/backend/scripts/entrypoint.sh"]

# Expose ports
EXPOSE 10012
EXPOSE 9012
