# One image for the whole app: the React build plus the Flask API that
# serves it, so the deployed app is a single URL (R2-3, #37).
#
# Cloud hosts like Render build this file themselves; nobody needs Docker
# installed locally.

# Stage 1: build the React page.
FROM node:22-alpine AS frontend
WORKDIR /app/creator-eaas
COPY creator-eaas/package.json creator-eaas/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY creator-eaas/ ./
RUN npm run build

# Stage 2: run the API, which also serves the page built above.
FROM python:3.12-slim
WORKDIR /app
COPY server/requirements.txt server/
RUN pip install --no-cache-dir -r server/requirements.txt
COPY server/ server/
COPY --from=frontend /app/creator-eaas/build creator-eaas/build

# The host serves over HTTPS, so the sign-in cookie can be HTTPS-only.
# Cloud hosts set PORT; 8000 is only the fallback for `docker run`.
ENV PORT=8000 \
    SESSION_COOKIE_SECURE=1 \
    FRONTEND_BUILD_DIR=/app/creator-eaas/build
EXPOSE 8000
CMD gunicorn --chdir server --bind 0.0.0.0:$PORT --workers 2 --timeout 60 "app:create_app()"
