import json
import logging

from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def run_generation(
    log_id: int, system_prompt: str, user_prompt: str, generation_type: str
) -> None:
    """
    Job APScheduler — ejecuta la llamada a la API de IA fuera del ciclo request/response.

    Evita que generaciones largas (full_post) excedan el timeout del proxy/gateway
    (Cloudflare / DigitalOcean App Platform), que corta la conexión y devuelve una
    página de error no-JSON antes de que la respuesta del modelo esté lista.

    Cualquier excepción no prevista también se captura: un job que muere sin tocar
    el log deja la fila en PENDING para siempre y el frontend termina mostrando
    "tardando demasiado" en vez del error real.
    """
    from .client import AIClientError, active_model, generate
    from .models import AIGenerationLog
    from .prompts import get_schema

    log = AIGenerationLog.objects.get(pk=log_id)
    log.model_used = active_model()

    try:
        schema = get_schema(generation_type)
        raw_text, input_tokens, output_tokens = generate(system_prompt, user_prompt, schema)
    except ImproperlyConfigured as exc:
        log.status = AIGenerationLog.STATUS_ERROR
        log.error_message = str(exc)
        log.save()
        return
    except AIClientError as exc:
        log.status = AIGenerationLog.STATUS_ERROR
        log.error_message = str(exc)
        log.save()
        return
    except Exception as exc:  # noqa: BLE001 — último resguardo: nunca dejar el job en pending.
        logger.exception("Fallo no previsto en run_generation (log_id=%s)", log_id)
        log.status = AIGenerationLog.STATUS_ERROR
        log.error_message = f"Error interno inesperado: {exc}"
        log.save()
        return

    log.input_tokens = input_tokens
    log.output_tokens = output_tokens

    # Los modelos sin structured outputs (DO Gradient) suelen envolver el JSON
    # en bloques ```json ... ```; con Anthropic + schema esto ya no ocurre, pero
    # se deja como red de seguridad.
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
        log.save()
        return

    log.status = AIGenerationLog.STATUS_DONE
    log.result_data = data
    log.success = True
    log.save()
