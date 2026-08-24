from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('carrito/', views.carrito_compra, name='carrito'),
    path('carrito/<int:pelicula_pk>/', views.carrito_compra, name='carrito_pelicula'),
    path('confirmacion/', views.confirmacion_compra, name='confirmacion_compra'),
    path('exito/', views.compra_exitosa, name='compra_exitosa'),
]
