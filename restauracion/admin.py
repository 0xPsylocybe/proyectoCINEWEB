"""Registro de productos, categorias y ventas en el Django Admin."""

from django.contrib import admin

from .models import Categoria, Producto, VentaProducto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Administración de categorías de productos de restauración."""
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Administración de productos del bar/cafetería del cine."""
    list_display = ("nombre", "categoria", "precio")
    search_fields = ("nombre",)
    list_filter = ("categoria",)


@admin.register(VentaProducto)
class VentaProductoAdmin(admin.ModelAdmin):
    """Administración y registro de ventas de productos de restauración."""
    list_display = ("id", "producto", "cantidad", "total_venta")
