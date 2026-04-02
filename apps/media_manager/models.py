from django.db import models
from django.conf import settings
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from apps.core.models import TimeStampedModel


class MediaFile(TimeStampedModel):
    TYPE_IMAGE = "image"
    TYPE_VIDEO = "video"
    TYPE_CHOICES = [
        (TYPE_IMAGE, "Imagen"),
        (TYPE_VIDEO, "Video"),
    ]

    file_type = models.CharField(
        "tipo",
        max_length=10,
        choices=TYPE_CHOICES,
        db_index=True,
    )

    # Campo para imágenes — usa ImageField para que imagekit pueda generar specs
    image = models.ImageField(
        "imagen",
        upload_to="media/images/%Y/%m/",
        null=True,
        blank=True,
        help_text="Subir solo si el tipo es Imagen.",
    )

    # Campo para videos propios (archivos subidos directamente)
    video_file = models.FileField(
        "archivo de video",
        upload_to="media/videos/%Y/%m/",
        null=True,
        blank=True,
        help_text="Subir solo si el tipo es Video y no se usa embed externo.",
    )

    # URL de embed externo (YouTube, Vimeo, etc.)
    video_embed_url = models.URLField(
        "URL embed de video",
        blank=True,
        help_text="URL de embed de YouTube o Vimeo. Alternativa al archivo de video.",
    )

    title = models.CharField("título", max_length=200)
    alt_text = models.CharField(
        "texto alternativo",
        max_length=200,
        blank=True,
        help_text="Descripción para accesibilidad y SEO de imágenes.",
    )
    caption = models.TextField("pie de foto/video", blank=True)

    # Metadatos de imagen (poblados automáticamente al guardar)
    width = models.PositiveIntegerField("ancho (px)", null=True, blank=True)
    height = models.PositiveIntegerField("alto (px)", null=True, blank=True)
    file_size = models.PositiveIntegerField("tamaño (bytes)", null=True, blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="subido por",
        related_name="media_files",
    )

    # Versiones WebP generadas automáticamente por imagekit (lazy)
    image_thumb_webp = ImageSpecField(
        source="image",
        processors=[ResizeToFit(400, 300)],
        format="WEBP",
        options={"quality": 85},
    )
    image_md_webp = ImageSpecField(
        source="image",
        processors=[ResizeToFit(800, 600)],
        format="WEBP",
        options={"quality": 85},
    )
    image_lg_webp = ImageSpecField(
        source="image",
        processors=[ResizeToFit(1280, 960)],
        format="WEBP",
        options={"quality": 85},
    )

    class Meta:
        verbose_name = "archivo de media"
        verbose_name_plural = "archivos de media"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_image(self):
        return self.file_type == self.TYPE_IMAGE

    @property
    def is_video(self):
        return self.file_type == self.TYPE_VIDEO

    def save(self, *args, **kwargs):
        # Poblar dimensiones y tamaño de imagen al crear
        if self.is_image and self.image and not self.width:
            try:
                from PIL import Image as PILImage
                with PILImage.open(self.image) as img:
                    self.width, self.height = img.size
            except Exception:
                pass
        if self.is_image and self.image and not self.file_size:
            try:
                self.file_size = self.image.size
            except Exception:
                pass
        super().save(*args, **kwargs)
