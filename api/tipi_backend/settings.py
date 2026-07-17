"""Configuración del backend, dirigida por variables de entorno (12-factor).

Este módulo se versiona en el repo (a diferencia del `settings.py` por-despliegue
del stack tipi original, que estaba en `.gitignore`) porque el monorepo necesita
un arranque reproducible: todos los valores salen del entorno con defaults que
coinciden con `docker-compose.yml`. No se incrustan secretos aquí; las claves y
credenciales viajan por variables de entorno (`LLM_API_KEY`, `MONGO_PASSWORD`,
`CACHE_REDIS_PASSWORD`, ...).
"""

from os import environ as env


def _as_bool(value: str) -> bool:
    return str(value).strip().lower() in ("1", "true", "yes", "on")


class Config:
    # --- Metadatos / servidor ---
    IP = env.get("IP", "0.0.0.0")
    PORT = int(env.get("PORT", "8080"))
    # Reutiliza el flag histórico FLASK_DEBUG del stack tipi como "modo desarrollo"
    # (activa el reload de uvicorn). No implica Flask: el backend es FastAPI.
    FLASK_DEBUG = _as_bool(env.get("FLASK_DEBUG", "False"))

    # País cuyos managers de tipo/estatus de iniciativa se cargan
    # (`tipi_backend/api/managers/<country>/`). México se añade en la fase F1;
    # por defecto "spain" para no romper import de managers en F0.
    COUNTRY = env.get("COUNTRY", "spain")

    # Sistema de alertas por correo (requiere config SparkPost). Desactivado por
    # defecto para que el stack arranque sin credenciales de correo.
    USE_ALERTS = _as_bool(env.get("USE_ALERTS", "False"))

    # Tamaño máximo de subida (bytes) admitido por el middleware de la API.
    # Default 20 MB; documentos legislativos rara vez lo superan.
    MAX_CONTENT_LENGTH = int(env.get("MAX_CONTENT_LENGTH", str(20 * 1024 * 1024)))

    # --- Tagger ---
    # Umbral de palabras a partir del cual el etiquetado se despacha como tarea
    # Celery asíncrona en vez de correr síncrono.
    TAGGER_MAX_WORDS = int(env.get("TAGGER_MAX_WORDS", "5000"))

    # --- Caché (Redis) ---
    CACHE = {
        "CACHE_REDIS_HOST": env.get("CACHE_REDIS_HOST", "redis"),
        "CACHE_REDIS_PORT": int(env.get("CACHE_REDIS_PORT", "6379")),
        "CACHE_REDIS_PASSWORD": env.get("CACHE_REDIS_PASSWORD", ""),
        "CACHE_REDIS_DB": int(env.get("CACHE_REDIS_DB_NAME", "8")),
    }
    # Claves de caché por recurso (mismos TTL/uso que el stack tipi original).
    CACHE_TAGS = "tipi_cache_tags"
    CACHE_DEPUTIES = "tipi_cache_deputies"
    CACHE_DEPUTIES_COMPACT = "tipi_cache_deputies_compact"
    CACHE_GROUPS = "tipi_cache_groups"
