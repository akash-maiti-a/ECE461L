# One image for the whole app: the React build plus the Flask API that
# serves it. Works on Render, Heroku (container stack), Fly.io, Railway, etc.

# 1. Build the React page.
FROM node:20-alpine AS frontend
WORKDIR /app/creator-eaas
COPY creator-eaas/package.json creator-eaas/package-lock.json ./
RUN npm ci
COPY creator-eaas/ ./
RUN npm run build

# 2. Run the API, which also serves the page built above.
FROM python:3.12-slim
WORKDIR /app
COPY server/requirements.txt server/
RUN pip install --no-cache-dir -r server/requirements.txt
COPY server/ server/
COPY --from=frontend /app/creator-eaas/build creator-eaas/build

# Cloud hosts set PORT; 8000 is only the fallback for `docker run`.
ENV PORT=8000 SESSION_COOKIE_SECURE=1
EXPOSE 8000
CMD gunicorn --chdir server --bind 0.0.0.0:$PORT --workers 2 --timeout 60 "app:create_app()"
