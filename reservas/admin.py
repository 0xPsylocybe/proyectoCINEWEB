from django.contrib import admin
from .models import EntradaButaca, ReservaButaca, VentaEntrada


class EntradaButacaInline(admin.TabularInline):
    model = EntradaButaca
    extra = 0
    fields = ("fila", "numero")


@admin.register(VentaEntrada)
class VentaEntradaAdmin(admin.ModelAdmin):
    list_display = ("id", "sesion", "cantidad", "precio_unitario", "total_venta", "asientos")
    list_filter = ("sesion__sala", "sesion__horario")
    search_fields = ("sesion__pelicula__titulo",)
    readonly_fields = ("total_venta",)
    inlines = [EntradaButacaInline]

    def asientos(self, obj):
        return ", ".join(b.etiqueta for b in obj.butacas.all()) or "—"
    asientos.short_description = "Butacas"


@admin.register(ReservaButaca)
class ReservaButacaAdmin(admin.ModelAdmin):
    list_display = ("etiqueta", "sesion", "expira_en", "caducada")
    list_filter = ("sesion__sala",)
