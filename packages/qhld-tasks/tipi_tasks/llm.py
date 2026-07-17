"""Abstracción mínima de proveedor LLM para la codificación NormTrace.

Proveedores reales (`anthropic`, `openai`) se llaman por HTTP con la librería
estándar (sin SDKs de pago como dependencia). El proveedor por defecto es
`mock`, que NO pasa por aquí: el codificador heurístico local vive en
`normtrace.py`. Así el sistema corre y se testea sin clave ni tokens, y las
llamadas reales quedan activables por variables de entorno.
"""

import json
import urllib.request

from . import config


class LLMError(RuntimeError):
    pass


def complete(system: str, user: str) -> str:
    """Devuelve el texto de la respuesta del proveedor configurado.

    Solo se invoca cuando LLM_PROVIDER es un proveedor real; el modo `mock`
    se resuelve en `normtrace.py` sin llegar aquí.
    """
    provider = config.LLM_PROVIDER
    if not config.LLM_API_KEY:
        raise LLMError(
            f"LLM_PROVIDER={provider} requiere LLM_API_KEY (no configurada)."
        )
    if provider == "anthropic":
        return _anthropic(system, user)
    if provider == "openai":
        return _openai(system, user)
    raise LLMError(f"Proveedor LLM no soportado: {provider!r}")


def _post_json(url: str, headers: dict, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=config.LLM_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _anthropic(system: str, user: str) -> str:
    base = config.LLM_API_BASE or "https://api.anthropic.com"
    model = config.LLM_MODEL or "claude-sonnet-5"
    body = _post_json(
        f"{base}/v1/messages",
        {
            "content-type": "application/json",
            "x-api-key": config.LLM_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        {
            "model": model,
            "max_tokens": 1024,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
    )
    try:
        return "".join(
            block.get("text", "")
            for block in body["content"]
            if block.get("type") == "text"
        )
    except (KeyError, TypeError) as e:
        raise LLMError(f"Respuesta inesperada de Anthropic: {e}")


def _openai(system: str, user: str) -> str:
    base = config.LLM_API_BASE or "https://api.openai.com"
    model = config.LLM_MODEL or "gpt-4o-mini"
    body = _post_json(
        f"{base}/v1/chat/completions",
        {
            "content-type": "application/json",
            "authorization": f"Bearer {config.LLM_API_KEY}",
        },
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
        },
    )
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise LLMError(f"Respuesta inesperada de OpenAI: {e}")
