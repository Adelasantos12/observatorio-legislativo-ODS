FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends git gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app/packages/qhld-tasks

# Contexto de build = raíz del monorepo (Railway: root dir "/"). Copiar todo
# packages/ trae tanto el código de qhld-tasks como el path-dep qhld-data.
COPY packages /app/packages

# Sync en dos pasos para cachear dependencias; el segundo instala tipi_tasks.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

CMD ["celery", "-A", "tipi_tasks", "worker", "-B", "-l", "info"]
