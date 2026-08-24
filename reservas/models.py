from datetime import timedelta

from django.db import models
from django.utils import timezone

# Minutos que se mantiene bloqueada una butaca desde que se elige.
MINUTOS_RESERVA = 30


class VentaEntrada(models.Model):
    """Venta de una entrada. Compra anónima (sin usuario)."""

    sesion = models.ForeignKey(
        "cartelera.Sesion",
        on_delete=models.PROTECT,
        related_name="entradas_vendidas",
        verbose_name="Sesión",
        null=True,
        blank=True,
    )
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad de entradas")
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2, default=10.00, verbose_name="Precio unitario")
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total")

    class Meta:
        db_table = "venta_entrada"
        verbose_name = "Venta de entrada"
        verbose_name_plural = "Ventas de entradas"

    def __str__(self):
        return f"{self.cantidad} entradas - {self.sesion.pelicula.titulo} ({self.total_venta}€)"


class EntradaButaca(models.Model):
    """Butaca vendida. La sesión se repite aquí para poder garantizar en la
    propia base de datos que una butaca no se vende dos veces."""

    venta = models.ForeignKey(
        VentaEntrada,
        on_delete=models.CASCADE,
        related_name="butacas",
    )
    sesion = models.ForeignKey(
        "cartelera.Sesion",
        on_delete=models.PROTECT,
        related_name="butacas_vendidas",
        verbose_name="Sesión",
    )
    fila = models.PositiveIntegerField("Fila")
    numero = models.PositiveIntegerField("Butaca")

    class Meta:
        db_table = "entrada_butaca"
        verbose_name = "Butaca vendida"
        verbose_name_plural = "Butacas vendidas"
        ordering = ["fila", "numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["sesion", "fila", "numero"],
                name="butaca_unica_por_sesion",
            )
        ]

    def __str__(self):
        return self.etiqueta

    @property
    def etiqueta(self):
        """Nombre legible de la butaca: fila 1 butaca 7 -> 'A7'."""
        return f"{chr(ord('A') + self.fila - 1)}{self.numero}"


class ReservaButaca(models.Model):
    """Bloqueo temporal de una butaca mientras el comprador termina el proceso.

    Caduca a los MINUTOS_RESERVA minutos; las caducadas se borran antes de
    consultar o reservar, de modo que la butaca vuelve a quedar libre sola.
    """

    sesion = models.ForeignKey(
        "cartelera.Sesion",
        on_delete=models.CASCADE,
        related_name="butacas_reservadas",
        verbose_name="Sesión",
    )
    fila = models.PositiveIntegerField("Fila")
    numero = models.PositiveIntegerField("Butaca")
    session_key = models.CharField("Comprador", max_length=40, db_index=True)
    expira_en = models.DateTimeField("Expira")

    class Meta:
        db_table = "reserva_butaca"
        verbose_name = "Butaca reservada"
        verbose_name_plural = "Butacas reservadas"
        ordering = ["fila", "numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["sesion", "fila", "numero"],
                name="reserva_unica_por_sesion",
            )
        ]

    def __str__(self):
        return f"{self.etiqueta} (hasta {self.expira_en:%H:%M})"

    @property
    def etiqueta(self):
        return f"{chr(ord('A') + self.fila - 1)}{self.numero}"

    @property
    def caducada(self):
        return self.expira_en <= timezone.now()

    @staticmethod
    def limpiar_caducadas():
        """Libera las butacas cuyo bloqueo ya expiró."""
        ReservaButaca.objects.filter(expira_en__lte=timezone.now()).delete()

    @staticmethod
    def nueva_expiracion():
        return timezone.now() + timedelta(minutes=MINUTOS_RESERVA)
