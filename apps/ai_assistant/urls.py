from django.urls import path
from . import views

app_name = "ai_assistant"

urlpatterns = [
    path("generate/", views.GenerateContentView.as_view(), name="generate"),
    path("generate/<int:job_id>/status/", views.GenerationStatusView.as_view(), name="generation_status"),
]
