from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse

from apps.seo.sitemaps import StaticViewSitemap
from apps.blog.sitemaps import PostSitemap, CategorySitemap

sitemaps = {
    "static": StaticViewSitemap,
    "posts": PostSitemap,
    "categories": CategorySitemap,
}


def _gone(request, *args, **kwargs):
    """410 Gone — URLs del dominio anterior (e-commerce) que Google aún tiene indexadas."""
    return HttpResponse(status=410)


urlpatterns = [
    path("admin/ai/", include("apps.ai_assistant.urls")),
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", include("apps.pages.urls")),
    path("blog/", include("apps.blog.urls")),
    path("servicios/", include("apps.services.urls")),
    # URLs del sitio anterior — devuelve 410 Gone para que Google las elimine del índice
    re_path(r"^shopping/", _gone),
    re_path(r"^authentic/", _gone),
    re_path(r"^shop/", _gone),
    re_path(r"^header\.php", _gone),
    re_path(r"^https:/", _gone),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
