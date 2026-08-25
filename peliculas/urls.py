from django.urls import path
from . import views

urlpatterns=[
    path("buscar_tmdb/", views.buscar_tmdb, name="buscar_tmdb"),
    path("cartel/<int:pk>/", views.cartel_pelicula, name="cartel_pelicula"),
    path("lista_peliculas",views.lista_peliculas, name="lista_peliculas"),
    path("nueva_pelicula", views.crear_pelicula,name="nueva_pelicula"),
    path("pelicula/<int:pk>/eliminar_pelicula",views.eliminar_pelicula, name="eliminar_pelicula"),
    path("pelicula/<int:pk>/editar_pelicual",views.editar_peliculas,name="editar_pelicula"),
]