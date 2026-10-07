"""Diagnostic: verify Anthropic API auth and model availability.

Uses the key from Django settings in-process. The key itself is never printed —
only HTTP status codes and (non-secret) error bodies. Makes only free GET calls
to /v1/models, so it consumes no tokens and costs nothing.

Run with:
    .venv/bin/python manage.py shell < scripts/diag_anthropic.py
"""

import json

import requests
from django.conf import settings

MODELS_TO_CHECK = [
    "claude-3-5-sonnet-20241022",  # hardcoded in apps/ai_assistant/client.py
    "claude-sonnet-4-6",  # seen in production AIGenerationLog rows
    "claude-opus-5-5",
    "claude-sonnet-5-5",
]

key = getattr(settings, "ANTHROPIC_API_KEY", "") or ""
print("AI_PROVIDER:", getattr(settings, "AI_PROVIDER", "<unset>"))
print("ANTHROPIC_API_KEY configured:", bool(key))
print("DO_MODEL_ACCESS_KEY configured:", bool(getattr(settings, "DO_MODEL_ACCESS_KEY", "")))

if not key:
    print("\nNo key in settings — nothing further to check.")
else:
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}

    def get(path):
        try:
            response = requests.get(
                f"https://api.anthropic.com/v1/{path}", headers=headers, timeout=30
            )
            return response.status_code, response.text
        except requests.RequestException as exc:
            return "NETWORK_ERROR", str(exc)[:300]

    print("\n--- auth check: GET /v1/models ---")
    status, body = get("models?limit=20")
    print("status:", status)
    if status == 200:
        print("available model ids:")
        for model in json.loads(body).get("data", []):
            print("   ", model["id"])
    else:
        print("body:", body[:400])

    print("\n--- model availability ---")
    for model_id in MODELS_TO_CHECK:
        status, body = get(f"models/{model_id}")
        note = "" if status == 200 else f"  {body[:200]}"
        print(f"{status}  {model_id}{note}")
