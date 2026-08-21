from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("sobrecine/", views.sobrecine, name="sobrecine"),
    path("proximos_estrenos/", views.proximos_estrenos, name="proximos_estrenos"),
]