from django.contrib import admin
from .models import  DetallePelicula, Director, Genero, Peliculas

@admin.action(description="Marcar como disponibles")
def marcar_disponibles(modeladmin, request, queryset):
    queryset.update(disponible=True)


@admin.action(description="Marcar como no disponibles")
def marcar_no_disponibles(modeladmin, request, queryset):
    queryset.update(disponible=False)


@admin.action(description="Marcar seleccionados como en cartelera")
def marcar_en_cartelera(modeladmin, request, queryset):
    queryset.update(en_cartelera=True)


@admin.action(description="Marcar seleccionados como fuera de cartelera")
def marcar_fuera_de_cartelera(modeladmin, request, queryset):
    queryset.update(en_cartelera=False)


@admin.action(description="Marcar seleccionados como destacados")
def marcar_destacados(modeladmin, request, queryset):
    queryset.update(destacada=True)


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ("nombre",)


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("nombre",)


class DetallePeliculaInline(admin.StackedInline): 
    model = DetallePelicula
    can_delete = False
    verbose_name_plural = "Detalles de la película"

@admin.register(Peliculas)
class PeliculasAdmin(admin.ModelAdmin):
    list_display = ("titulo", "duracion", "director", "genero", "anio", "recaudacion")
    search_fields = ("titulo", "genero__nombre", "director__nombre")
    list_filter = ("genero", "director", "anio")
    readonly_fields = ("recaudacion",)
    inlines = [DetallePeliculaInline] 


@admin.register(DetallePelicula)
class DetallePeliculaAdmin(admin.ModelAdmin):
    list_display = ( "pelicula","clasificacion","destacada","en_cartelera","fecha_estreno",)
    list_filter = ("clasificacion", "destacada", "en_cartelera", "fecha_estreno")
    search_fields = ("pelicula__titulo",)
    list_editable = ("destacada", "en_cartelera")
    actions = [
        marcar_en_cartelera,
        marcar_fuera_de_cartelera,
        marcar_destacados,
    ]

