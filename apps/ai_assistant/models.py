from django.conf import settings
from django.db import models


class AIGenerationLog(models.Model):
    TYPE_CHOICES = [
        ("full_post", "Artículo completo"),
        ("meta_only", "Solo metadatos SEO"),
        ("excerpt", "Resumen"),
        ("improve", "Mejora de texto"),
        ("alt_text", "Texto alternativo"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="usuario",
    )
    generation_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="tipo de generación",
    )
    site_target = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="sitio destino",
    )
    model_used = models.CharField(
        max_length=100,
        verbose_name="modelo usado",
    )
    input_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name="tokens de entrada",
    )
    output_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name="tokens de salida",
    )
    success = models.BooleanField(
        default=True,
        verbose_name="exitoso",
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="mensaje de error",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creación",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "registro de generación IA"
        verbose_name_plural = "registros de generación IA"

    def __str__(self) -> str:
        status = "OK" if self.success else "ERROR"
        return f"[{status}] {self.get_generation_type_display()} — {self.created_at:%d/%m/%Y %H:%M}"
