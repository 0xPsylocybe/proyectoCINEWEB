from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_cartelera, name='cartelera'),
    path('detalle/<int:pk>/', views.detalle_cartelera, name='detalle_cartelera'),

    # CRUD Sesiones
    path('sesiones/', views.lista_sesiones, name='sesiones_lista'),
    path('sesiones/nueva/', views.crear_sesion, name='sesion_form'),
    path('sesiones/<int:pk>/editar/', views.editar_sesion, name='editar_sesion'),
    path('sesiones/<int:pk>/eliminar/', views.eliminar_sesion, name='eliminar_sesion'),
    path('sesiones/rellenar_sesiones/', views.rellenar_sesiones, name='rellenar_sesiones'),
]