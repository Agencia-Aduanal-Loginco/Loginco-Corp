import json

import groq as groq_lib
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from .client import MODEL, generate
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
            success=False,  # Se actualiza a True si todo va bien
        )

        # 4. Construir prompts
        try:
            system_prompt, user_prompt = build_prompt(generation_type, context)
        except ValueError as exc:
            log.error_message = str(exc)
            log.save()
            return JsonResponse({"error": str(exc)}, status=400)

        # 5. Llamar a la API de Claude
        try:
            raw_text, input_tokens, output_tokens = generate(system_prompt, user_prompt)
        except ImproperlyConfigured:
            log.error_message = "ANTHROPIC_API_KEY no configurada."
            log.save()
            return JsonResponse(
                {"error": "API key no configurada en el servidor."},
                status=503,
            )
        except groq_lib.APIError as exc:
            log.error_message = str(exc)
            log.save()
            return JsonResponse(
                {"error": "Error al comunicarse con la API de IA."},
                status=502,
            )

        # 6. Parsear JSON de la respuesta de la IA
        # Los modelos open source suelen envolver el JSON en bloques ```json ... ```
        clean_text = raw_text.strip()
        if clean_text.startswith("```"):
            # Elimina la primera línea (```json o ```) y el cierre (```)
            lines = clean_text.splitlines()
            clean_text = "\n".join(lines[1:])
            if clean_text.rstrip().endswith("```"):
                clean_text = clean_text.rstrip()[:-3].rstrip()

        try:
            data = json.loads(clean_text, strict=False)
        except (json.JSONDecodeError, ValueError):
            log.error_message = f"La IA devolvió texto no parseable como JSON: {raw_text[:500]}"
            log.input_tokens = input_tokens
            log.output_tokens = output_tokens
            log.save()
            return JsonResponse(
                {"error": "La IA devolvió una respuesta no procesable."},
                status=502,
            )

        # 7. Guardar log exitoso
        log.input_tokens = input_tokens
        log.output_tokens = output_tokens
        log.success = True
        log.save()

        # 8. Incrementar contador de sesión
        request.session[SESSION_KEY] = count + 1

        # 9. Respuesta exitosa
        generations_remaining = MAX_GENERATIONS_PER_SESSION - (count + 1)
        return JsonResponse(
            {
                "success": True,
                "data": data,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                },
                "generations_remaining": generations_remaining,
            }
        )
