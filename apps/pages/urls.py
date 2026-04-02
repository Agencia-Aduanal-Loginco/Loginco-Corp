from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("nosotros/", views.AboutView.as_view(), name="about"),
    path("contacto/", views.ContactView.as_view(), name="contact"),
    path("robots.txt", views.RobotsTxtView.as_view(), name="robots_txt"),
]
