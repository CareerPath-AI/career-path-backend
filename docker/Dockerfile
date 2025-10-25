FROM python:3.12-slim-bookworm

RUN apt-get update && \
    apt-get install -y curl vim netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.7.9 /uv /uvx /bin/

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY ./.env.docker ./.env
COPY ./app ./app
COPY alembic.ini ./
COPY migrations ./migrations

RUN uv sync --locked

CMD ["sh", "-c", " \
  while ! nc -z career-path-postgres 5432; do sleep 1; done; \
  /app/.venv/bin/alembic upgrade head && \
  /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 \
"]