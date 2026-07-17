FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git gcc poppler-utils tesseract-ocr tesseract-ocr-spa tesseract-ocr-cat antiword \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app/api

# --- Contexto de build = raíz del monorepo (Railway: root dir "/") ---
# 1) Path-deps editables (qhld-data, qhld-tasks) referenciados como ../packages/*.
COPY packages /app/packages
# 2) Manifiesto + lock del api primero, para cachear la capa de dependencias.
COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --locked --no-install-project --no-dev
# 3) Código del backend y sync final (instala el propio qhld-backend).
COPY api/ /app/api/
RUN uv sync --locked --no-dev

# 4) Diccionario (seeds + load_kb.py) y datos NormTrace (catálogos ODS/metas +
#    CSV semilla del Ejecutivo): los usan los pasos de carga en Railway
#    (`load_kb.py`, `load_executive.py`) y el API para servir catálogos.
COPY knowledgebase /app/knowledgebase
COPY normtrace /app/normtrace

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080
# Railway inyecta $PORT; caemos a 8080 en local. --proxy-headers para ir tras el
# proxy de Railway (sustituye a ProxyFix de Flask).
CMD ["sh", "-c", "uvicorn tipi_backend.wsgi:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips '*'"]
