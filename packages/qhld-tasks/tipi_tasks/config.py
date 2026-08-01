from os import environ as env
from pathlib import Path

from tipi_data.redis_url import resolve_broker, resolve_cache


DEBUG = env.get('DEBUG', 'False') == 'True'
# Broker/backend: un BROKER autenticado puesto a mano manda; un BROKER heredado
# sin contraseña cede ante REDIS_URL (autenticada) para no bloquear Railway; sin
# nada, el default local. Ver resolve_broker.
BROKER = resolve_broker(env.get('BROKER'), 2, 'redis://redis:6379/2')
RESULT_BACKEND = resolve_broker(env.get('RESULT_BACKEND'), 3, 'redis://redis:6379/3')

# --- NormTrace (codificación estructural por LLM, fase F4) --------------------
# Proveedor de LLM. "mock" (por defecto) usa un codificador heurístico local
# determinista: no requiere clave ni dependencias de pago, y deja el sistema
# ejecutable y testeable sin gastar tokens. "anthropic" | "openai" | "gemini"
# llaman al proveedor real vía HTTP usando LLM_API_KEY. Con LLM_MODEL se elige el
# modelo (p. ej. gemini-1.5-flash, gemini-2.0-flash, gpt-4o-mini, claude-sonnet-5).
LLM_PROVIDER = env.get('LLM_PROVIDER', 'mock')
LLM_MODEL = env.get('LLM_MODEL', '')
LLM_API_KEY = env.get('LLM_API_KEY', '')
LLM_API_BASE = env.get('LLM_API_BASE', '')  # opcional, para gateways/compatibles
LLM_TIMEOUT = int(env.get('LLM_TIMEOUT', '60'))

# Presupuesto: nº máximo de unidades a codificar por documento (corta documentos
# enormes). Lo excedente se reporta como units_skipped.
NORMTRACE_MAX_UNITS = int(env.get('NORMTRACE_MAX_UNITS', '50'))

# Versión del prompt: participa en la clave de caché (hash de unidad + versión)
# para invalidar la caché cuando cambia el prompt.
NORMTRACE_PROMPT_VERSION = env.get('NORMTRACE_PROMPT_VERSION', 'v1')

# Directorio del "cerebro jurídico" mexicano del que se leen extractos para el
# prompt (no se parafrasean a mano). En contenedor, definir NORMTRACE_BRAIN_DIR.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_BRAIN_DIR = str(
    _REPO_ROOT / "normtrace" / "02_country_legal_brains" / "mexico"
)
NORMTRACE_BRAIN_DIR = env.get('NORMTRACE_BRAIN_DIR', _DEFAULT_BRAIN_DIR)

# Esquema JSON contra el que valida cada salida de la codificación.
_DEFAULT_SCHEMA = str(
    _REPO_ROOT / "normtrace" / "schemas_runtime" / "unit_analysis.schema.json"
)
NORMTRACE_SCHEMA = env.get('NORMTRACE_SCHEMA', _DEFAULT_SCHEMA)

# --- PAIL-MX (análisis ex ante de iniciativas; módulo seleccionable) ----------
# Rulebook (43 verificaciones) y esquema de salida: fuente de verdad de la autora
# en normtrace/schemas_runtime/; el motor los LEE, nunca los edita.
PAIL_PROTOCOL = env.get('PAIL_PROTOCOL', str(
    _REPO_ROOT / "normtrace" / "schemas_runtime" / "pail_protocol.json"))
PAIL_SCHEMA = env.get('PAIL_SCHEMA', str(
    _REPO_ROOT / "normtrace" / "schemas_runtime" / "pail_dictamen.schema.json"))
# Ruta de los índices del corpus CRN (manifest/articles/crossrefs.json). Por
# defecto los lee de normtrace/crn_indices/ (índices compactos ~6 MB que SÍ van al
# repo y viajan en la imagen); el VAULT de origen (315 leyes .md) no va a git. Se
# puede sobreescribir con PAIL_INDICES_PATH (p. ej. un volumen). Si la carpeta no
# existe o está vacía, la capa CSN degrada sola a NO_VERIFICABLE (lo maneja el
# motor, no se envuelve). Ver docs/DEPLOY_RAILWAY.md.
PAIL_INDICES_PATH = env.get('PAIL_INDICES_PATH', str(
    _REPO_ROOT / "normtrace" / "crn_indices"))
# Tope de llamadas LLM por dictamen en la pasada de juicio (control de costo).
PAIL_LLM_MAX_JUICIOS = int(env.get('PAIL_LLM_MAX_JUICIOS', '40'))
# Concurrencia de la pasada de juicio: las verificaciones se resuelven en paralelo
# para no exceder el tiempo de la petición HTTP con decenas de llamadas seguidas.
PAIL_LLM_CONCURRENCY = int(env.get('PAIL_LLM_CONCURRENCY', '6'))

TEMPLATE_DIR = env.get('TEMPLATE_DIR', None)
# validation timeout in days
VALIDATION_TIMEOUT = int(env.get('VALIDATION_TIMEOUT', '30'))
# Timeout to run the clean email task every X seconds
CLEAN_EMAILS_TIMEOUT = int(env.get('CLEAN_EMAILS_TIMEOUT', '300'))

ALERT_BANNER_URL = env.get('ALERT_BANNER_URL', '')

CACHE_REDIS_DB = int(env.get('CACHE_REDIS_DB_NAME', '8'))
CACHE_REDIS_HOST, CACHE_REDIS_PORT, CACHE_REDIS_PASSWORD = resolve_cache(
    env.get('CACHE_REDIS_HOST'), env.get('CACHE_REDIS_PORT'), env.get('CACHE_REDIS_PASSWORD'))

SCANNED_TEXT_EXCERPT_SIZE = int(env.get('SCANNED_TEXT_EXCERPT_SIZE', '500'))

def mail_config(kb):
    roots = {
            'politicas': 'TIPI',
            'ods': 'P2030',
            'escaner': 'SCANNER'
            }

    fields = [
            'NAME',
            'FROM',
            'DESCRIPTION',
            'EMAIL',
            'FRONTEND',
            'BACKEND',
            'COLOR',
            'API',
            'BANNER_URL',
            'ALERT_SUBJECT',
            'VALIDATION_SUBJECT',
            ]

    root = roots[kb]
    configuration = {}

    for field in fields:
        key = root + '_' + field
        configuration[field] = env.get(key)

    return configuration
