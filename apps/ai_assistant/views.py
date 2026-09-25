import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from apps.core.scheduler import get_scheduler

from .client import MODEL
from .jobs import run_generation
from .models import AIGenerationLog
from .prompts import build_prompt

ALLOWED_TYPES = {"full_post", "meta_only", "excerpt", "improve", "alt_text"}
MAX_GENERATIONS_PER_SESSION = 3
SESSION_KEY = "ai_generation_count"


@method_decorator(staff_member_required, name="dispatch")
class GenerateContentView(View):
    """
    Endpoint AJAX para el asistente IA en el Django Admin.
    Acepta POST con JSON body: {generation_type, context}.
    Retorna JSON con el contenido generado o un mensaje de error.
    """

    def post(self, request, *args, **kwargs):
        # 1. Parsear JSON del body
        try:
            payload = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "El cuerpo de la solicitud no es JSON válido."}, status=400)

        # 2. Validar generation_type
        generation_type = payload.get("generation_type", "")
        if generation_type not in ALLOWED_TYPES:
            return JsonResponse(
                {
                    "error": f"Tipo de generación '{generation_type}' no válido. "
                    f"Tipos permitidos: {', '.join(sorted(ALLOWED_TYPES))}."
                },
                status=400,
            )

        # 3. Rate limiting via sesión
        count = request.session.get(SESSION_KEY, 0)
        if count >= MAX_GENERATIONS_PER_SESSION:
            return JsonResponse(
                {
                    "error": "Límite de generaciones alcanzado. Recarga la página para continuar.",
                    "generations_remaining": 0,
                },
                status=429,
            )

        context = payload.get("context", {})
        site_target = context.get("site_target_name", context.get("site_target_slug", ""))

        # Preparar log (se guarda siempre, incluso en error)
        log = AIGenerationLog(
            user=request.user if request.user.is_authenticated else None,
            generation_type=generation_type,
            site_target=site_target,
            model_used=MODEL,
            status=AIGenerationLog.STATUS_PENDING,
            success=False,  # Se actualiza a True si todo va bien
        )

        # 4. Construir prompts
        try:
            system_prompt, user_prompt = build_prompt(generation_type, context)
        except ValueError as exc:
            log.status = AIGenerationLog.STATUS_ERROR
            log.error_message = str(exc)
            log.save()
            return JsonResponse({"error": str(exc)}, status=400)

        log.save()

        # 5. Encolar la llamada a la API de IA como job en background.
        # full_post puede tardar 30-90s+, más que el timeout del proxy/gateway
        # (Cloudflare / DigitalOcean App Platform) — por eso no se espera aquí.
        get_scheduler().add_job(
            run_generation,
            trigger="date",
            run_date=timezone.now(),
            args=[log.pk, system_prompt, user_prompt],
            id=f"ai_generation_{log.pk}",
            replace_existing=True,
            misfire_grace_time=60,
        )

        # 6. Incrementar contador de sesión (el intento consume la cuota)
        request.session[SESSION_KEY] = count + 1
        generations_remaining = MAX_GENERATIONS_PER_SESSION - (count + 1)

        return JsonResponse(
            {
                "job_id": log.pk,
                "generations_remaining": generations_remaining,
            },
            status=202,
        )


@method_decorator(staff_member_required, name="dispatch")
class GenerationStatusView(View):
    """
    Endpoint de polling — el frontend consulta el estado de un job de generación
    encolado por GenerateContentView hasta que termine (done/error).
    """

    def get(self, request, job_id, *args, **kwargs):
        try:
            log = AIGenerationLog.objects.get(pk=job_id)
        except AIGenerationLog.DoesNotExist as exc:
            raise Http404("Job de generación no encontrado.") from exc

        if log.status == AIGenerationLog.STATUS_PENDING:
            return JsonResponse({"status": "pending"})

        if log.status == AIGenerationLog.STATUS_ERROR:
            return JsonResponse({"status": "error", "error": log.error_message})

        return JsonResponse(
            {
                "status": "done",
                "data": log.result_data,
                "tokens": {
                    "input": log.input_tokens,
                    "output": log.output_tokens,
                },
            }
        )
