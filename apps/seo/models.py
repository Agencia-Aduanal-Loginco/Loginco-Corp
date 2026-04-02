from django.db import models


class SEOMixin(models.Model):
    """
    Mixin abstracto para cualquier modelo público con necesidades SEO.
    Proporciona campos para meta tags, Open Graph, canonical URL y JSON-LD.
    """

    meta_title = models.CharField(
        "meta título",
        max_length=70,
        blank=True,
        help_text="Título para buscadores. Máximo 70 caracteres.",
    )
    meta_description = models.TextField(
        "meta descripción",
        max_length=160,
        blank=True,
        help_text="Descripción para buscadores. Máximo 160 caracteres.",
    )
    meta_keywords = models.CharField(
        "palabras clave",
        max_length=255,
        blank=True,
        help_text="Palabras clave separadas por comas.",
    )
    og_title = models.CharField(
        "título Open Graph",
        max_length=95,
        blank=True,
        help_text="Título para redes sociales. Si se deja vacío se usa meta_title.",
    )
    og_description = models.TextField(
        "descripción Open Graph",
        max_length=200,
        blank=True,
        help_text="Descripción para redes sociales. Si se deja vacío se usa meta_description.",
    )
    canonical_url = models.URLField(
        "URL canónica",
        blank=True,
        help_text="URL canónica. Dejar vacío para usar la URL actual.",
    )
    no_index = models.BooleanField(
        "no indexar",
        default=False,
        help_text="Marcar para excluir esta página de los motores de búsqueda.",
    )
    schema_markup = models.JSONField(
        "JSON-LD Schema.org",
        default=dict,
        blank=True,
        help_text="Markup estructurado en formato JSON-LD. Se inserta automáticamente en <head>.",
    )

    class Meta:
        abstract = True

    def get_effective_meta_title(self):
        """Retorna meta_title o fallback al campo 'title' del modelo."""
        return self.meta_title or getattr(self, "title", "")

    def get_effective_og_title(self):
        return self.og_title or self.get_effective_meta_title()

    def get_effective_og_description(self):
        return self.og_description or self.meta_description
