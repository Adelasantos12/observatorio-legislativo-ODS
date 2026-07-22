"""Deriva la configuración de Redis desde variables de entorno estándar.

Los PaaS (Railway, etc.) exponen la instancia de Redis como `REDIS_URL` con
credenciales embebidas (`redis://default:PASS@host:port`). Cuando el despliegue
no fija `BROKER`/`RESULT_BACKEND`/`CACHE_REDIS_*` de forma explícita, se derivan
de ahí (o de las variables por componente `REDISHOST/REDISPORT/REDISPASSWORD/
REDISUSER`) para que el worker y el api se autentiquen sin construir a mano URLs
con contraseña y sufijo de base de datos.

Sin ninguna de esas variables (p. ej. docker-compose local) todo cae a los
valores por defecto históricos (`redis://redis:6379`), así que no cambia el
comportamiento local.
"""

from os import environ as env
from urllib.parse import urlsplit, urlunsplit


def redis_base():
    """URL base de Redis (esquema + credenciales + host + puerto, sin `/db`).

    Devuelve None si no hay configuración de entorno (se usarán los defaults).
    """
    url = (
        env.get("REDIS_URL")
        or env.get("REDIS_PRIVATE_URL")
        or env.get("REDIS_PUBLIC_URL")
    )
    if url:
        p = urlsplit(url)
        return urlunsplit((p.scheme or "redis", p.netloc, "", "", ""))
    host = env.get("REDISHOST")
    if host:
        port = env.get("REDISPORT", "6379")
        user = env.get("REDISUSER", "default")
        pwd = env.get("REDISPASSWORD")
        auth = f"{user}:{pwd}@" if pwd else ""
        return f"redis://{auth}{host}:{port}"
    return None


def redis_url_for_db(db, default):
    """URL de Redis para una base concreta, o `default` si no hay config de entorno."""
    base = redis_base()
    return f"{base}/{db}" if base else default


def _has_credentials(url):
    return isinstance(url, str) and "@" in url


def resolve_broker(explicit, db, default):
    """Elige la URL de Redis correcta dando prioridad a las credenciales.

    Precedencia:
      1. `explicit` (BROKER/RESULT_BACKEND) si trae credenciales (`user:pass@`):
         una URL autenticada puesta a mano siempre se respeta.
      2. La derivada de `REDIS_URL`/`REDISHOST` (con credenciales) si existe:
         así, un `explicit` heredado sin contraseña (p. ej. el viejo
         `redis://redis:6379/2`) NO bloquea la conexión autenticada — basta
         añadir `REDIS_URL` y el worker levanta, sin cazar variables viejas.
      3. `explicit` sin credenciales, si no hay nada derivado.
      4. `default` (docker-compose local: `redis://redis:6379/N`).
    """
    if _has_credentials(explicit):
        return explicit
    derived = redis_url_for_db(db, None)
    if derived:
        return derived
    return explicit or default


def redis_parts():
    """(host, port, password, user) derivados de la config de entorno.

    Todos None cuando no hay configuración (el llamador usa sus defaults).
    """
    base = redis_base()
    if not base:
        return None, None, None, None
    p = urlsplit(base)
    return p.hostname, (p.port or 6379), (p.password or None), (p.username or None)


def resolve_cache(explicit_host, explicit_port, explicit_pwd,
                  default_host="redis", default_port=6379):
    """(host, port, password) para el cliente de caché, priorizando credenciales.

    Si hay `CACHE_REDIS_PASSWORD` explícito se respeta toda la config manual; si
    no, se prefieren las partes derivadas de `REDIS_URL` (autenticadas) sobre un
    `CACHE_REDIS_HOST` heredado sin contraseña; sin nada, los defaults locales.
    """
    if explicit_pwd:
        return (explicit_host or default_host, int(explicit_port or default_port), explicit_pwd)
    host, port, pwd, _ = redis_parts()
    if host:
        return (host, int(port or default_port), pwd or "")
    return (explicit_host or default_host, int(explicit_port or default_port), "")
