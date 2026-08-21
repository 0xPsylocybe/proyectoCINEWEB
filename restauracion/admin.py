from django.contrib import admin

from .models import Producto, VentaProducto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio")
    search_fields = ("nombre",)


@admin.register(VentaProducto)
class VentaProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "producto", "cantidad", "total_venta")
