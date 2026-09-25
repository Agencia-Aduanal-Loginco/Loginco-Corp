import json
import logging

import openai
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def run_generation(log_id: int, system_prompt: str, user_prompt: str) -> None:
    """
    Job APScheduler — ejecuta la llamada a la API de IA fuera del ciclo request/response.

    Evita que generaciones largas (full_post) excedan el timeout del proxy/gateway
    (Cloudflare / DigitalOcean App Platform), que corta la conexión y devuelve una
    página de error no-JSON antes de que la respuesta del modelo esté lista.
    """
    from .client import generate
    from .models import AIGenerationLog

    log = AIGenerationLog.objects.get(pk=log_id)

    try:
        raw_text, input_tokens, output_tokens = generate(system_prompt, user_prompt)
    except ImproperlyConfigured:
        log.status = AIGenerationLog.STATUS_ERROR
        log.error_message = "DO_MODEL_ACCESS_KEY no configurada."
        log.save()
        return
    except openai.APIError as exc:
        log.status = AIGenerationLog.STATUS_ERROR
        log.error_message = str(exc)
        log.save()
        return

    # Los modelos open source suelen envolver el JSON en bloques ```json ... ```
    clean_text = raw_text.strip()
    if clean_text.startswith("```"):
        lines = clean_text.splitlines()
        clean_text = "\n".join(lines[1:])
        if clean_text.rstrip().endswith("```"):
            clean_text = clean_text.rstrip()[:-3].rstrip()

    try:
        data = json.loads(clean_text, strict=False)
    except (json.JSONDecodeError, ValueError):
        log.status = AIGenerationLog.STATUS_ERROR
        log.error_message = f"La IA devolvió texto no parseable como JSON: {raw_text[:500]}"
        log.input_tokens = input_tokens
        log.output_tokens = output_tokens
        log.save()
        return

    log.status = AIGenerationLog.STATUS_DONE
    log.result_data = data
    log.input_tokens = input_tokens
    log.output_tokens = output_tokens
    log.success = True
    log.save()
