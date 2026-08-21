from django.db import models


class CaracteristicaSala(models.Model):
    """Característica de una sala (3D, IMAX, Dolby Atmos, VOSE...)."""

    nombre = models.CharField(max_length=80)

    class Meta:
        db_table = "caracteristica_sala"
        verbose_name = "Característica de sala"
        verbose_name_plural = "Características de sala"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Sala(models.Model):
    """Sala física del cine. Cada sala tiene una característica (N:1)."""

    caracteristica = models.ForeignKey(
        CaracteristicaSala,
        on_delete=models.PROTECT,
        related_name="salas",
    )
    capacidad = models.PositiveIntegerField()
    duracion_maxima = models.PositiveIntegerField(
        help_text="Duración máxima de proyección admitida, en minutos",
    )
    precio_entrada = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = "sala"
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

    def __str__(self):
        return f"Sala {self.pk} ({self.caracteristica})"


class Sesion(models.Model):
    """Sesión: una película proyectada en una sala.

    Por decisión de diseño, los horarios se gestionan en la lógica del programa
    y no en la BBDD, por eso el modelo solo relaciona película y sala.
    """

    pelicula = models.ForeignKey(
        "peliculas.Pelicula",
        on_delete=models.CASCADE,
        related_name="sesiones",
    )
    sala = models.ForeignKey(
        Sala,
        on_delete=models.PROTECT,
        related_name="sesiones",
    )

    class Meta:
        db_table = "sesion"
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"

    def __str__(self):
        return f"{self.pelicula} en {self.sala}"
