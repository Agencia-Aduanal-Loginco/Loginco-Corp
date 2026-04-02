from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import AIGenerationLog


@admin.register(AIGenerationLog)
class AIGenerationLogAdmin(ModelAdmin):
    list_display = [
        "generation_type",
        "site_target",
        "user",
        "model_used",
        "input_tokens",
        "output_tokens",
        "success",
        "created_at",
    ]
    list_filter = ["generation_type", "success", "created_at"]
    readonly_fields = [f.name for f in AIGenerationLog._meta.get_fields()]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
