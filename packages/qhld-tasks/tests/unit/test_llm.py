"""Tests del conector LLM: ruteo por proveedor y parseo de respuesta."""

import pytest

from tipi_tasks import config, llm


def test_gemini_rutea_y_parsea(monkeypatch):
    """LLM_PROVIDER=gemini pega al endpoint de Google, manda la clave por header
    x-goog-api-key, el system como system_instruction y temperatura 0; y extrae
    el texto de candidates[0].content.parts."""
    captured = {}

    def fake_post(url, headers, payload):
        captured.update(url=url, headers=headers, payload=payload)
        return {"candidates": [{"content": {"parts": [{"text": "OK-gemini"}]}}]}

    monkeypatch.setattr(config, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(config, "LLM_API_KEY", "secreta")
    monkeypatch.setattr(config, "LLM_MODEL", "gemini-1.5-flash")
    monkeypatch.setattr(llm, "_post_json", fake_post)

    out = llm.complete("sistema-blindaje", "usuario")

    assert out == "OK-gemini"
    assert "generativelanguage.googleapis.com" in captured["url"]
    assert "gemini-1.5-flash:generateContent" in captured["url"]
    assert captured["headers"]["x-goog-api-key"] == "secreta"
    assert "secreta" not in captured["url"]  # la clave no viaja en la URL
    assert captured["payload"]["system_instruction"]["parts"][0]["text"] == "sistema-blindaje"
    assert captured["payload"]["generationConfig"]["temperature"] == 0


def test_gemini_respuesta_inesperada_es_error(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(config, "LLM_API_KEY", "x")
    monkeypatch.setattr(llm, "_post_json", lambda u, h, p: {"error": "bloqueado"})
    with pytest.raises(llm.LLMError):
        llm.complete("s", "u")


def test_proveedor_no_soportado_es_error(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "cohere")
    monkeypatch.setattr(config, "LLM_API_KEY", "x")
    with pytest.raises(llm.LLMError):
        llm.complete("s", "u")


def test_sin_clave_es_error(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(config, "LLM_API_KEY", "")
    with pytest.raises(llm.LLMError):
        llm.complete("s", "u")
