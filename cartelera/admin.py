from django.contrib import admin
from .models import CaracteristicasSala, Sala, PeliculasEnSala

@admin.register(CaracteristicaSala)
class CaracteristicaSalaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ("identificador", "capacidad", "tiempo_max", "get_caracteristicas")
    list_filter = ("caracteristicas",)
    filter_horizontal = ("caracteristicas",)

    def get_caracteristicas(self, obj):
        return ", ".join([c.nombre for c in obj.caracteristicas.all()])
    get_caracteristicas.short_description = 'Características'

@admin.register(PeliculasEnSala)
class PeliculasEnSalaAdmin(admin.ModelAdmin):
    list_display = ("pelicula", "sala", "horario")
    list_filter = ("sala", "horario")
    search_fields = ("pelicula__titulo", "sala__identificador")
from .models import CaracteristicaSala, Sala, Sesion


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ("id", "pelicula", "sala")
    list_filter = ("sala",)
    search_fields = ("pelicula__titulo",)
