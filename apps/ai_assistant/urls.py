from django.urls import path
from . import views

app_name = "ai_assistant"

urlpatterns = [
    path("generate/", views.GenerateContentView.as_view(), name="generate"),
]
