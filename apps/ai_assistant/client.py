"""
Cliente singleton AI.
Selector de proveedores: Anthropic (via requests) o DO Gradient.
"""

import requests
import openai
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DO_INFERENCE_URL = "https://inference.do-ai.run/v1/"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

MODEL_DO = "openai-gpt-oss-20b"
MODEL_ANTHROPIC = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 4096

def generate(system: str, user: str) -> tuple[str, int, int]:
    """
    Envía solicitud a proveedor configurado.
    """
    provider = getattr(settings, "AI_PROVIDER", "do_gradient")

    if provider == "anthropic":
        api_key = getattr(settings, "ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ImproperlyConfigured("ANTHROPIC_API_KEY no configurada.")

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": MODEL_ANTHROPIC,
            "max_tokens": MAX_TOKENS,
            "system": system,
            "messages": [{"role": "user", "content": user}]
        }
        response = requests.post(ANTHROPIC_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"], data["usage"]["input_tokens"], data["usage"]["output_tokens"]

    elif provider == "do_gradient":
        api_key = getattr(settings, "DO_MODEL_ACCESS_KEY", "")
        if not api_key:
            raise ImproperlyConfigured("DO_MODEL_ACCESS_KEY no configurada.")

        client = openai.OpenAI(base_url=DO_INFERENCE_URL, api_key=api_key)
        completion = client.chat.completions.create(
            model=MODEL_DO,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return completion.choices[0].message.content, completion.usage.prompt_tokens, completion.usage.completion_tokens

    raise ImproperlyConfigured(f"Proveedor no soportado: {provider}")
