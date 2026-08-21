from django.urls import path
from . import views

urlpatterns=[
    path('cartelera/', views.lista_cartelera, name='cartelera'),
    path("detalle_cartelera",views.detalle_cartelera, name="detalle_cartelera")
    ]