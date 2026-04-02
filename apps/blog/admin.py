from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Category, Post, SiteTarget, Tag
from .widgets import TiptapWidget


@admin.register(SiteTarget)
class SiteTargetAdmin(ModelAdmin):
    list_display = ["name", "domain", "slug", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "domain"]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "slug", "post_count"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["site_targets"]
    search_fields = ["name"]

    @admin.display(description="Publicaciones")
    def post_count(self, obj):
        return obj.posts.count()


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ["title", "status", "category", "site_targets_display", "ai_generated", "reading_time", "published_at"]
    list_filter = ["status", "category", "site_targets", "ai_generated", "created_at"]
    search_fields = ["title", "excerpt", "body"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["tags", "site_targets"]
    readonly_fields = ["reading_time", "created_at", "updated_at"]
    date_hierarchy = "published_at"

    class Media:
        css = {"all": ["css/tiptap-editor.css"]}
        js = ["js/tiptap-bundle.js", "js/ai-assistant.js"]

    fieldsets = (
        ("Contenido", {
            "fields": (
                "title", "slug", "excerpt", "body",
                "featured_image", "video_url",
            ),
        }),
        ("Clasificación", {
            "fields": ("category", "tags", "site_targets"),
        }),
        ("Publicación", {
            "fields": ("status", "published_at", "author"),
        }),
        ("SEO", {
            "fields": (
                "meta_title", "meta_description", "meta_keywords",
                "og_title", "og_description",
                "canonical_url", "no_index", "schema_markup",
            ),
            "classes": ("collapse",),
        }),
        ("Info", {
            "fields": ("ai_generated", "reading_time", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "body" in form.base_fields:
            form.base_fields["body"].widget = TiptapWidget()
        return form

    def get_changeform_initial_data(self, request):
        return {"author": request.user}

    @admin.display(description="Sitios destino")
    def site_targets_display(self, obj):
        return ", ".join(obj.site_targets.values_list("name", flat=True))
