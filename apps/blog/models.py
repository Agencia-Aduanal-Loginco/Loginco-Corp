from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.seo.models import SEOMixin


class SiteTarget(models.Model):
    """
    Sub-sitio al que puede pertenecer una publicación.
    Permite al CMS centralizar contenido y asignarlo a uno o más dominios.
    """

    name = models.CharField("nombre", max_length=100)
    domain = models.URLField("dominio", help_text="ej: https://agencia-aduanal.loginco.com.mx")
    slug = models.SlugField(unique=True)
    description = models.TextField("descripción", blank=True)
    is_active = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "sitio destino"
        verbose_name_plural = "sitios destino"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(TimeStampedModel):
    name = models.CharField("nombre", max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField("descripción", blank=True)
    site_targets = models.ManyToManyField(
        SiteTarget,
        blank=True,
        verbose_name="sitios destino",
        related_name="categories",
    )

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField("nombre", max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "etiqueta"
        verbose_name_plural = "etiquetas"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(SEOMixin, TimeStampedModel):
    STATUS_DRAFT = "draft"
    STATUS_SCHEDULED = "scheduled"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Borrador"),
        (STATUS_SCHEDULED, "Programado"),
        (STATUS_PUBLISHED, "Publicado"),
    ]

    title = models.CharField("título", max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    excerpt = models.TextField(
        "resumen",
        max_length=300,
        help_text="Descripción corta para listados y redes sociales. Máximo 300 caracteres.",
    )
    body = models.TextField(
        "contenido",
        help_text="Contenido HTML generado por el editor TipTap.",
    )

    featured_image = models.ForeignKey(
        "media_manager.MediaFile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="imagen destacada",
        related_name="featured_posts",
        limit_choices_to={"file_type": "image"},
    )
    video_url = models.URLField(
        "URL de video",
        blank=True,
        help_text="URL embed de YouTube o Vimeo para incluir en el artículo.",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="categoría",
        related_name="posts",
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="etiquetas", related_name="posts")
    site_targets = models.ManyToManyField(
        SiteTarget,
        verbose_name="sitios destino",
        related_name="posts",
        help_text="Sub-sitio(s) en los que aparecerá esta publicación.",
    )

    status = models.CharField(
        "estado",
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField(
        "fecha de publicación",
        null=True,
        blank=True,
        help_text="Dejar vacío para publicar inmediatamente al cambiar estado a Publicado.",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="autor",
        related_name="posts",
    )

    ai_generated = models.BooleanField(
        "generado con IA",
        default=False,
        help_text="Indica si el contenido fue generado o asistido por la IA.",
    )
    reading_time = models.PositiveSmallIntegerField(
        "tiempo de lectura (min)",
        default=0,
        help_text="Calculado automáticamente al guardar.",
    )

    class Meta:
        verbose_name = "publicación"
        verbose_name_plural = "publicaciones"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        # Calcular tiempo de lectura (promedio 200 palabras/min)
        if self.body:
            word_count = len(self.body.split())
            self.reading_time = max(1, round(word_count / 200))

        # Establecer published_at al publicar si no está definido
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED
