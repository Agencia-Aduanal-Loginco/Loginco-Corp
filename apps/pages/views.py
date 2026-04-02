from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView

from apps.blog.models import Post


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recent_posts"] = (
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .select_related("category", "featured_image")
            .order_by("-published_at")[:6]
        )
        return ctx


class AboutView(TemplateView):
    template_name = "pages/about.html"


class ContactView(TemplateView):
    template_name = "pages/contact.html"


class RobotsTxtView(View):
    """
    Sirve /robots.txt de forma dinámica.
    Bloquea el admin y declara el sitemap principal.
    """

    _CONTENT = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "\n"
        "Sitemap: https://loginco.com.mx/sitemap.xml\n"
    )

    def get(self, request):
        return HttpResponse(self._CONTENT, content_type="text/plain; charset=utf-8")
