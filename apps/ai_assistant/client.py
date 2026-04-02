"""
Cliente singleton para la API de Groq.
Carga lazy de la instancia — no falla en import si la key no está configurada.
"""

import groq as groq_lib
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 4096

_client: groq_lib.Groq | None = None


def _get_client() -> groq_lib.Groq:
    """Retorna la instancia singleton del cliente Groq, creándola si es necesario."""
    global _client
    if _client is None:
        api_key = getattr(settings, "GROQ_API_KEY", "")
        if not api_key:
            raise ImproperlyConfigured(
                "GROQ_API_KEY no está configurada. "
                "Agrega la variable en tu archivo .env para usar el asistente IA."
            )
        _client = groq_lib.Groq(api_key=api_key)
    return _client


def generate(system: str, user: str) -> tuple[str, int, int]:
    """
    Envía una solicitud a la API de Groq y retorna la respuesta.

    Args:
        system: Prompt del sistema con instrucciones y contexto de marca.
        user: Prompt del usuario con los datos específicos de la solicitud.

    Returns:
        Tupla (text, input_tokens, output_tokens) donde text es la respuesta
        de texto generada por el modelo.

    Raises:
        ImproperlyConfigured: Si GROQ_API_KEY no está configurada.
        groq_lib.APIError: Si ocurre un error en la comunicación con la API.
    """
    client = _get_client()
    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    text = completion.choices[0].message.content
    input_tokens = completion.usage.prompt_tokens
    output_tokens = completion.usage.completion_tokens
    return text, input_tokens, output_tokens
