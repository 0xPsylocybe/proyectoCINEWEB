from django.urls import path
from . import views

urlpatterns=[
    path("peliculas/lista_peliculas",views.lista_peliculas, name="lista_peliculas"),
    path("peliculas/nueva_pelicula", views.crear_pelicula,name="nueva_pelicula"),
    path("pelicula/<int:pk>/eliminar_pelicula",views.eliminar_pelicula, name="eliminar_pelicula"),
    path("pelicula/<int:pk>/editar_pelicual",views.editar_peliculas,name="editar_pelicula"),
    path("pelicula/<int:pk>/detalle_pelicual", views.detalle_pelicula,name="detalle_pelicula"),
]