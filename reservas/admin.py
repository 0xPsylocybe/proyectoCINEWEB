"""Registro de ventas de entradas y reservas de butacas en el Django Admin."""

from django.contrib import admin
from .models import EntradaButaca, ReservaButaca, VentaEntrada


class EntradaButacaInline(admin.TabularInline):
    """Formulario en línea para visualizar las butacas asignadas a una venta."""
    model = EntradaButaca
    extra = 0
    fields = ("fila", "numero")


@admin.register(VentaEntrada)
class VentaEntradaAdmin(admin.ModelAdmin):
    """Administración de ventas de entradas con detalle de sesión, recaudación y butacas ocupadas."""
    list_display = ("id", "sesion", "cantidad", "precio_unitario", "total_venta", "asientos")
    list_filter = ("sesion__sala", "sesion__horario")
    search_fields = ("sesion__pelicula__titulo",)
    readonly_fields = ("total_venta",)
    inlines = [EntradaButacaInline]

    def asientos(self, obj):
        """Devuelve un listado de las etiquetas de las butacas vendidas en la transacción."""
        return ", ".join(b.etiqueta for b in obj.butacas.all()) or "—"
    asientos.short_description = "Butacas"


@admin.register(ReservaButaca)
class ReservaButacaAdmin(admin.ModelAdmin):
    """Administración y supervisión de las reservas temporales de butacas activas."""
    list_display = ("etiqueta", "sesion", "expira_en", "caducada")
    list_filter = ("sesion__sala",)
