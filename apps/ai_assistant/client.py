"""
Cliente singleton para DigitalOcean AI Platform (Gradient).
Soporta proveedores Anthropic (Claude) y DO Gradient (Llama).
"""

import openai
from anthropic import Anthropic
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DO_INFERENCE_URL = "https://inference.do-ai.run/v1/"
MODEL_DO = "openai-gpt-oss-20b"
MODEL_ANTHROPIC = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 4096

def generate(system: str, user: str) -> tuple[str, int, int]:
    """
    Envía solicitud a proveedor configurado y retorna respuesta.
    """
    provider = getattr(settings, "AI_PROVIDER", "do_gradient")

    if provider == "anthropic":
        api_key = getattr(settings, "ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ImproperlyConfigured("ANTHROPIC_API_KEY no configurada.")

        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model=MODEL_ANTHROPIC,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        # Anthropic SDK token usage requires manual access, ignoring temporarily for bare generation
        return message.content[0].text, 0, 0

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
