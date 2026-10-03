"""
Cliente singleton AI.
Selector de proveedores: Anthropic (via openai bridge) o DO Gradient.
"""

import openai
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DO_INFERENCE_URL = "https://inference.do-ai.run/v1/"
ANTHROPIC_URL = "https://api.anthropic.com/v1/"

MODEL_DO = "openai-gpt-oss-20b"
MODEL_ANTHROPIC = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 4096

def generate(system: str, user: str) -> tuple[str, int, int]:
    """
    Envía solicitud a proveedor configurado usando cliente openai.
    """
    provider = getattr(settings, "AI_PROVIDER", "do_gradient")

    if provider == "anthropic":
        api_key = getattr(settings, "ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ImproperlyConfigured("ANTHROPIC_API_KEY no configurada.")

        # Anthropic endpoint via openai client
        client = openai.OpenAI(base_url=ANTHROPIC_URL, api_key=api_key)
        completion = client.chat.completions.create(
            model=MODEL_ANTHROPIC,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return completion.choices[0].message.content, completion.usage.prompt_tokens, completion.usage.completion_tokens

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
