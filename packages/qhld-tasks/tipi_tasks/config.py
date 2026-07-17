from os import environ as env
from pathlib import Path


DEBUG = env.get('DEBUG', 'False') == 'True'
BROKER = env.get('BROKER', 'redis://redis:6379/2')
RESULT_BACKEND = env.get('RESULT_BACKEND', 'redis://redis:6379/3')

# --- NormTrace (codificación estructural por LLM, fase F4) --------------------
# Proveedor de LLM. "mock" (por defecto) usa un codificador heurístico local
# determinista: no requiere clave ni dependencias de pago, y deja el sistema
# ejecutable y testeable sin gastar tokens. "anthropic"/"openai" llaman al
# proveedor real vía HTTP usando LLM_API_KEY.
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

TEMPLATE_DIR = env.get('TEMPLATE_DIR', None)
# validation timeout in days
VALIDATION_TIMEOUT = int(env.get('VALIDATION_TIMEOUT', '30'))
# Timeout to run the clean email task every X seconds
CLEAN_EMAILS_TIMEOUT = int(env.get('CLEAN_EMAILS_TIMEOUT', '300'))

ALERT_BANNER_URL = env.get('ALERT_BANNER_URL', '')

CACHE_REDIS_DB = int(env.get('CACHE_REDIS_DB_NAME', '8'))
CACHE_REDIS_HOST = env.get('CACHE_REDIS_HOST', 'redis')
CACHE_REDIS_PORT = int(env.get('CACHE_REDIS_PORT', '6379'))

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
