from django.views.generic import TemplateView


class ServicesIndexView(TemplateView):
    template_name = "services/index.html"
