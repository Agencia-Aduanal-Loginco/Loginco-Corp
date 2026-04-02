from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from apps.seo.sitemaps import StaticViewSitemap
from apps.blog.sitemaps import PostSitemap, CategorySitemap

sitemaps = {
    "static": StaticViewSitemap,
    "posts": PostSitemap,
    "categories": CategorySitemap,
}

urlpatterns = [
    path("admin/ai/", include("apps.ai_assistant.urls")),
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", include("apps.pages.urls")),
    path("blog/", include("apps.blog.urls")),
    path("servicios/", include("apps.services.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
