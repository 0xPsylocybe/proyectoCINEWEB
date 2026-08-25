"""Registro de salas y sesiones en el Django Admin."""

from django.contrib import admin
from .models import Sala, Sesion


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    """Administración de salas de proyección en el panel de control."""
    list_display = ("identificador", "tipo", "capacidad", "filas", "columnas", "precio_entrada")
    list_editable = ("filas", "columnas", "precio_entrada")



@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    """Administración de sesiones de cine y monitorización de tiempos de ocupación."""
    list_display = ("pelicula", "sala", "horario", "hora_fin_ocupacion")
    list_filter = ("sala", "horario")
    search_fields = ("pelicula__nombre", "sala__identificador")
    readonly_fields = ("tiempo_ocupacion_display",)
    fieldsets = (
        ("Información básica", {
            'fields': ('pelicula', 'sala', 'horario')
        }),
        ("Timeline de ocupación", {
            'fields': ('tiempo_ocupacion_display',),
            'description': 'Horarios automáticos basados en: 15 min publicidad + duración película + 20 min limpieza'
        }),
    )

    def hora_fin_ocupacion(self, obj):
        """Devuelve la hora en la que concluye la limpieza y la sala queda libre."""
        return obj.hora_fin_limpieza.strftime('%d/%m/%Y %H:%M')
    hora_fin_ocupacion.short_description = "Sala libre a las"

    def tiempo_ocupacion_display(self, obj):
        """Genera un bloque visual con el desglose de tiempos de la sesión."""
        html = f"""
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace;">
            <div><strong>📺 Publicidad:</strong> {obj.hora_inicio_publicidad.strftime('%H:%M')} - {obj.hora_inicio_pelicula.strftime('%H:%M')} (15 min)</div>
            <div><strong>🎬 Película:</strong> {obj.hora_inicio_pelicula.strftime('%H:%M')} - {obj.hora_fin_pelicula.strftime('%H:%M')} ({obj.pelicula.duracion} min)</div>
            <div><strong>🧹 Limpieza:</strong> {obj.hora_fin_pelicula.strftime('%H:%M')} - {obj.hora_fin_limpieza.strftime('%H:%M')} (20 min)</div>
            <hr>
            <div><strong>⏱️ Total ocupación:</strong> {int(obj.duracion_total_ocupacion)} minutos</div>
        </div>
        """
        return html
    tiempo_ocupacion_display.allow_tags = True
    tiempo_ocupacion_display.short_description = "Timeline de ocupación de sala"
