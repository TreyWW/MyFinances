# Dockerfile
FROM python:3.9-alpine

# Set the working directory
WORKDIR /myfinances
# Copy the project files
COPY . .

# Install dependencies
RUN apk add --update mariadb-connector-c-dev
RUN apk add --no-cache --virtual .build-deps py-pip musl-dev gcc mariadb-dev
RUN pip install --upgrade pip
RUN pip install mysql
RUN apk add --no-cache git
CMD ["git","--version"]
RUN pip install -r requirements.txt

# Set the entrypoint
#COPY ../scripts /infrastructure/scripts/
RUN chmod +x scripts/*
RUN chmod +x scripts/tests/*
ENTRYPOINT ["sh", "scripts/entrypoint.sh"]

# Expose ports
EXPOSE 10012
EXPOSE 9012
