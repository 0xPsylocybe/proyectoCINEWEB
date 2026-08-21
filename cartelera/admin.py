from django.contrib import admin
from .models import Sala, Sesion


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ("identificador", "capacidad", "tiempo_max", "tipo")



@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ("pelicula", "sala", "horario")
    list_filter = ("sala", "horario")
    search_fields = ("pelicula__nombre", "sala__identificador")
