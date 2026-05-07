from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from apps.blog.models import Post

from .forms import ContactForm


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


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("pages:contact")

    def form_valid(self, form):
        d = form.cleaned_data
        servicio_label = dict(form.fields["servicio"].choices).get(d.get("servicio", ""), "—")
        subject = f"[Loginco] Contacto de {d['nombre']} — {servicio_label}"
        body = (
            f"Nombre:   {d['nombre']}\n"
            f"Empresa:  {d.get('empresa') or '—'}\n"
            f"Correo:   {d['correo']}\n"
            f"Teléfono: {d.get('telefono') or '—'}\n"
            f"Servicio: {servicio_label}\n"
            f"\nMensaje:\n{d['mensaje']}"
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        messages.success(
            self.request,
            "¡Mensaje enviado! Te contactaremos en menos de 2 horas.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor corrige los errores marcados en el formulario.")
        return super().form_invalid(form)


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
