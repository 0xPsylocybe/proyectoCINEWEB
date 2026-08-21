from django.contrib import admin

from .models import CaracteristicaSala, Sala, Sesion


@admin.register(CaracteristicaSala)
class CaracteristicaSalaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ("id", "caracteristica", "capacidad", "precio_entrada")
    list_filter = ("caracteristica",)


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ("id", "pelicula", "sala")
    list_filter = ("sala",)
    search_fields = ("pelicula__titulo",)
