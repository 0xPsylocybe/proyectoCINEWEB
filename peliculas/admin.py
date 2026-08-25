"""Registro de peliculas, directores y generos en el Django Admin."""

from django.contrib import admin
from .models import CartelPelicula, DetallePelicula, Director, Genero, Peliculas

@admin.action(description="Marcar como disponibles")
def marcar_disponibles(modeladmin, request, queryset):
    """Acción de administración para marcar elementos como disponibles."""
    queryset.update(disponible=True)


@admin.action(description="Marcar como no disponibles")
def marcar_no_disponibles(modeladmin, request, queryset):
    """Acción de administración para marcar elementos como no disponibles."""
    queryset.update(disponible=False)


@admin.action(description="Marcar seleccionados como en cartelera")
def marcar_en_cartelera(modeladmin, request, queryset):
    """Acción de administración para marcar películas seleccionadas como activas en cartelera."""
    queryset.update(en_cartelera=True)


@admin.action(description="Marcar seleccionados como fuera de cartelera")
def marcar_fuera_de_cartelera(modeladmin, request, queryset):
    """Acción de administración para retirar películas seleccionadas de cartelera."""
    queryset.update(en_cartelera=False)


@admin.action(description="Marcar seleccionados como destacados")
def marcar_destacados(modeladmin, request, queryset):
    """Acción de administración para marcar películas seleccionadas como destacadas."""
    queryset.update(destacada=True)


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    """Administración de géneros de películas."""
    list_display = ("nombre",)


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    """Administración de directores de películas."""
    list_display = ("nombre",)


class DetallePeliculaInline(admin.StackedInline): 
    """Formulario en línea para editar los detalles de la película dentro de su ficha."""
    model = DetallePelicula
    can_delete = False
    verbose_name_plural = "Detalles de la película"

@admin.register(Peliculas)
class PeliculasAdmin(admin.ModelAdmin):
    """Administración de películas, su recaudación acumulada y verificación de póster."""
    list_display = ("titulo", "duracion", "director", "genero", "anio",
                    "recaudacion", "tiene_cartel")
    search_fields = ("titulo", "genero__nombre", "director__nombre")
    list_filter = ("genero", "director", "anio")
    readonly_fields = ("recaudacion",)
    inlines = [DetallePeliculaInline]

    @admin.display(boolean=True, description="Cartel")
    def tiene_cartel(self, obj):
        """El cartel se guarda en la BBDD, no en media/, para que se comparta."""
        return CartelPelicula.objects.filter(pelicula=obj).exists() 


@admin.register(DetallePelicula)
class DetallePeliculaAdmin(admin.ModelAdmin):
    """Administración de estados de cartelera, estreno y clasificación por edades."""
    list_display = ( "pelicula","clasificacion","destacada","en_cartelera","fecha_estreno",)
    list_filter = ("clasificacion", "destacada", "en_cartelera", "fecha_estreno")
    search_fields = ("pelicula__titulo",)
    list_editable = ("destacada", "en_cartelera")
    actions = [
        marcar_en_cartelera,
        marcar_fuera_de_cartelera,
        marcar_destacados,
    ]

