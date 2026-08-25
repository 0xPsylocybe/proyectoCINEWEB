"""Rutas del Snack Bar."""

from django.urls import path
from . import views

app_name = 'restauracion'

urlpatterns = [
    path('', views.catalogo_restauracion, name='catalogo'),
]
