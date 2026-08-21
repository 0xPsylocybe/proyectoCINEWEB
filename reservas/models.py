from django.db import models


class VentaEntrada(models.Model):
    """Venta de una entrada. Compra anónima (sin usuario).

    Según el esquema acordado, la entrada referencia la película y la sala
    directamente (no la sesión).
    """

    pelicula = models.ForeignKey(
        "peliculas.Pelicula",
        on_delete=models.PROTECT,
        related_name="entradas",
    )
    sala = models.ForeignKey(
        "cartelera.Sala",
        on_delete=models.PROTECT,
        related_name="entradas",
    )
    precio_venta = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        db_table = "venta_entrada"
        verbose_name = "Venta de entrada"
        verbose_name_plural = "Ventas de entradas"

    def __str__(self):
        return f"Entrada {self.pelicula} ({self.precio_venta})"
