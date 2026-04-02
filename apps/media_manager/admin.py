from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(ModelAdmin):
    list_display = [
        "preview_thumbnail",
        "title",
        "file_type",
        "dimensions_display",
        "file_size_display",
        "uploaded_by",
        "created_at",
    ]
    list_filter = ["file_type", "created_at"]
    search_fields = ["title", "alt_text"]
    readonly_fields = [
        "width",
        "height",
        "file_size",
        "created_at",
        "updated_at",
        "image_preview",
    ]

    fieldsets = (
        (
            "Archivo",
            {
                "fields": ("file_type", "image", "video_file", "video_embed_url"),
            },
        ),
        (
            "Metadatos",
            {
                "fields": ("title", "alt_text", "caption"),
            },
        ),
        (
            "Información técnica",
            {
                "fields": (
                    "image_preview",
                    "width",
                    "height",
                    "file_size",
                    "uploaded_by",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    # ------------------------------------------------------------------
    # Pre-rellenar uploaded_by con el usuario actual en alta nueva
    # ------------------------------------------------------------------

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("uploaded_by", request.user.pk)
        return initial

    def save_model(self, request, obj, form, change):
        """Garantiza que uploaded_by siempre quede poblado."""
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    # ------------------------------------------------------------------
    # Miniatura en list_display
    # ------------------------------------------------------------------

    @admin.display(description="")
    def preview_thumbnail(self, obj):
        """Miniatura de 48 px de alto en la lista; ícono de play para video."""
        if obj.is_image and obj.image:
            try:
                url = obj.image_thumb_webp.url
            except Exception:
                url = obj.image.url
            return format_html(
                '<img src="{}" alt="" style="height:48px;width:auto;'
                'border-radius:4px;object-fit:cover;">',
                url,
            )
        if obj.is_video:
            return format_html('<span style="font-size:1.5rem;" title="Video">&#9654;</span>')
        return "\u2014"

    # ------------------------------------------------------------------
    # Campos de display para list_display
    # ------------------------------------------------------------------

    @admin.display(description="Dimensiones")
    def dimensions_display(self, obj):
        """Muestra 'ancho\u00d7alto' si ambos están disponibles, o '\u2014'."""
        if obj.width and obj.height:
            return f"{obj.width}\u00d7{obj.height}"
        return "\u2014"

    @admin.display(description="Tamaño")
    def file_size_display(self, obj):
        """Convierte bytes a B / KB / MB con una cifra decimal."""
        if not obj.file_size:
            return "\u2014"
        size = obj.file_size
        if size < 1_024:
            return f"{size} B"
        if size < 1_048_576:
            return f"{size / 1_024:.1f} KB"
        return f"{size / 1_048_576:.1f} MB"

    # ------------------------------------------------------------------
    # Vista previa de 300 px en el formulario de detalle (readonly_field)
    # ------------------------------------------------------------------

    @admin.display(description="Vista previa")
    def image_preview(self, obj):
        """
        Renderiza una imagen de máximo 300 px de ancho en el formulario
        de cambio. Devuelve '\u2014' si el archivo no es una imagen o no
        tiene archivo asociado.
        """
        if obj.is_image and obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="max-width:300px;height:auto;'
                'border-radius:4px;border:1px solid #d1d5db;">',
                obj.image.url,
                obj.alt_text or obj.title,
            )
        return "\u2014"
