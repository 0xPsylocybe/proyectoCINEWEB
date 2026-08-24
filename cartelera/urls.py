from django.urls import path
from . import views

urlpatterns=[
    path('', views.lista_cartelera, name='cartelera'),
    path('detalle/<int:pk>/', views.detalle_cartelera, name='detalle_cartelera'),
    ]