FROM python:3.12-slim

# git/gcc para compilar algunas deps; OCR (tesseract + poppler) para leer los
# dictámenes escaneados en normtrace-atribucion; antiword para .doc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git gcc poppler-utils tesseract-ocr tesseract-ocr-spa tesseract-ocr-cat antiword \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Contexto de build = raíz del monorepo (Railway: root dir "/"). El engine tiene
# path-deps a ../packages/*, así que hay que copiar packages/ y engine/ juntos.
WORKDIR /app/engine
COPY packages /app/packages
COPY engine /app/engine

RUN uv sync --locked --no-install-project --no-dev
# Instala el proyecto para que el console script `qhld` quede en el PATH.
RUN uv sync --locked --no-dev

# Los jobs leen los CSV/catálogos y el cerebro jurídico desde /app/normtrace.
COPY normtrace /app/normtrace

ENV PATH="/app/.venv/bin:$PATH"

# Servicio de jobs por lotes: el trabajo real se lanza como Pre-Deploy Command
# (p. ej. `qhld normtrace-atribucion`). El proceso principal solo mantiene vivo
# el contenedor para que el deploy quede sano.
CMD ["/bin/sh", "-c", "tail -f /dev/null"]
