# -------------------------------------
# 1) Builder Stage
# -------------------------------------
FROM node:23-alpine AS builder

# Work in root of the container
WORKDIR /app

# Accept ENV (default = dev)
ARG ENV=dev
ENV NODE_ENV=$ENV

# Copy only dependency manifests first
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the source
COPY . .

RUN npm run tailwind-build

# Build using the correct environment script
RUN npm run webpack-$ENV

# -------------------------------------
# 2) Nginx Final Stage
# -------------------------------------
FROM nginx:1.25-alpine

# Accept ENV again so it can be used in config
ARG ENV=dev
ENV APP_ENV=$ENV

# Install envsubst for dynamic config
RUN apk add --no-cache gettext

# Copy Nginx template from root (adjust path if directory differs)
COPY infrastructure/nginx/default.conf /etc/nginx/conf.d/default.conf.template

# Copy build output from builder
# Change the path here if dist folder is different
COPY --from=builder /app/ /srv/http/

EXPOSE 10012

# Use envsubst to replace variables in config at runtime
CMD ["/bin/sh", "-c", "envsubst '$APP_ENV' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]

# # For development
# docker build --build-arg ENV=dev -t myfinances-ui:dev .

# # For production
# docker build --build-arg ENV=prod -t myfinances-ui:prod .
