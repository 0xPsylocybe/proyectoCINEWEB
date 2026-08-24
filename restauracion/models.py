from django.db import models


class Categoria(models.Model):
    """Categoría de productos de restauración."""

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = "categoria"
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Producto de restauración (palomitas, refrescos, snacks...)."""

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos", verbose_name="Categoría", null=True, blank=True)

    class Meta:
        db_table = "producto"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class VentaProducto(models.Model):
    """Venta de un producto de restauración. Compra anónima (sin usuario)."""

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="ventas",
    )
    cantidad = models.PositiveIntegerField(default=1)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "venta_producto"
        verbose_name = "Venta de producto"
        verbose_name_plural = "Ventas de productos"

    def __str__(self):
        return f"{self.cantidad} x {self.producto} = {self.total_venta}"
