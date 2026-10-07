"""
Cliente AI del asistente de contenido.

Selector de proveedores: Anthropic (SDK oficial) o DigitalOcean Gradient
(endpoint compatible con OpenAI).

Todos los fallos del proveedor se traducen a `AIClientError` con un mensaje
legible en español, para que el job de APScheduler lo pueda registrar en
`AIGenerationLog.error_message` y el admin lo muestre tal cual.
"""

import logging

import anthropic
import openai
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

DO_INFERENCE_URL = "https://inference.do-ai.run/v1/"

MODEL_DO = "openai-gpt-oss-20b"
MODEL_ANTHROPIC = "claude-opus-5-5"

# El pensamiento extendido consume parte de max_tokens, por eso el margen amplio.
# Con streaming no hay riesgo de exceder el timeout de la petición HTTP.
MAX_TOKENS = 16000

# Timeout y reintentos del SDK de Anthropic. El job corre en background, así que
# un timeout generoso no bloquea ninguna petición del admin.
REQUEST_TIMEOUT_SECONDS = 300.0
MAX_RETRIES = 3


class AIClientError(Exception):
    """Fallo del proveedor de IA, ya traducido a un mensaje legible."""


def active_provider() -> str:
    return getattr(settings, "AI_PROVIDER", "do_gradient")


def active_model() -> str:
    """Identificador que se guarda en `AIGenerationLog.model_used`."""
    provider = active_provider()
    if provider == "anthropic":
        return f"anthropic:{MODEL_ANTHROPIC}"
    if provider == "do_gradient":
        return f"do_gradient:{MODEL_DO}"
    return provider


def generate(system: str, user: str, schema: dict | None = None) -> tuple[str, int, int]:
    """
    Envía la solicitud al proveedor configurado y devuelve (texto, tokens_entrada, tokens_salida).

    Args:
        system: System prompt.
        user: User prompt.
        schema: JSON Schema opcional. Con Anthropic activa structured outputs, lo que
            garantiza que la respuesta sea JSON válido con esa forma exacta. El
            proveedor DO Gradient lo ignora (no soporta la función).

    Raises:
        ImproperlyConfigured: Falta la API key del proveedor, o el proveedor no existe.
        AIClientError: El proveedor respondió con error o la conexión falló.
    """
    provider = active_provider()

    if provider == "anthropic":
        return _generate_anthropic(system, user, schema)
    if provider == "do_gradient":
        return _generate_do_gradient(system, user)

    raise ImproperlyConfigured(f"Proveedor de IA no soportado: {provider}")


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------


def _generate_anthropic(system: str, user: str, schema: dict | None) -> tuple[str, int, int]:
    api_key = getattr(settings, "ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ImproperlyConfigured("ANTHROPIC_API_KEY no configurada.")

    client = anthropic.Anthropic(
        api_key=api_key,
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_retries=MAX_RETRIES,
    )

    kwargs = {
        "model": MODEL_ANTHROPIC,
        "max_tokens": MAX_TOKENS,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "thinking": {"type": "adaptive"},
    }
    if schema is not None:
        kwargs["output_config"] = {"format": {"type": "json_schema", "schema": schema}}

    try:
        # Streaming: un artículo completo puede tardar minutos; sin streaming la
        # petición corre riesgo de timeout del lado del servidor.
        with client.messages.stream(**kwargs) as stream:
            message = stream.get_final_message()
    except anthropic.AuthenticationError as exc:
        raise AIClientError(
            "ANTHROPIC_API_KEY rechazada (401). La llave es inválida o fue revocada."
        ) from exc
    except anthropic.PermissionDeniedError as exc:
        raise AIClientError(
            f"Acceso denegado (403) al modelo {MODEL_ANTHROPIC}. "
            "La llave no tiene permiso sobre ese modelo."
        ) from exc
    except anthropic.NotFoundError as exc:
        raise AIClientError(
            f"El modelo '{MODEL_ANTHROPIC}' no existe o fue retirado (404). "
            "Actualiza MODEL_ANTHROPIC en apps/ai_assistant/client.py."
        ) from exc
    except anthropic.RateLimitError as exc:
        raise AIClientError(
            "Límite de tasa de Anthropic alcanzado (429). Espera un momento y reintenta."
        ) from exc
    except anthropic.APIStatusError as exc:
        # Incluye 400 por saldo insuficiente y 5xx del proveedor.
        raise AIClientError(f"Anthropic respondió {exc.status_code}: {exc.message}") from exc
    except anthropic.APIConnectionError as exc:
        raise AIClientError(f"No se pudo conectar con la API de Anthropic: {exc}") from exc

    text = "".join(block.text for block in message.content if block.type == "text")
    if not text.strip():
        raise AIClientError(
            f"Anthropic devolvió una respuesta sin texto (stop_reason={message.stop_reason})."
        )

    return text, message.usage.input_tokens, message.usage.output_tokens


# ---------------------------------------------------------------------------
# DigitalOcean Gradient
# ---------------------------------------------------------------------------


def _generate_do_gradient(system: str, user: str) -> tuple[str, int, int]:
    api_key = getattr(settings, "DO_MODEL_ACCESS_KEY", "")
    if not api_key:
        raise ImproperlyConfigured("DO_MODEL_ACCESS_KEY no configurada.")

    client = openai.OpenAI(
        base_url=DO_INFERENCE_URL,
        api_key=api_key,
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_retries=MAX_RETRIES,
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_DO,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
    except openai.APIStatusError as exc:
        raise AIClientError(f"DigitalOcean respondió {exc.status_code}: {exc.message}") from exc
    except openai.APIConnectionError as exc:
        raise AIClientError(f"No se pudo conectar con DigitalOcean Gradient: {exc}") from exc

    return (
        completion.choices[0].message.content,
        completion.usage.prompt_tokens,
        completion.usage.completion_tokens,
    )
