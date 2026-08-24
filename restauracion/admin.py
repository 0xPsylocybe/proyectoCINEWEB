from django.contrib import admin

from .models import Categoria, Producto, VentaProducto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio")
    search_fields = ("nombre",)
    list_filter = ("categoria",)


@admin.register(VentaProducto)
class VentaProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "producto", "cantidad", "total_venta")
