from django.db import models
from peliculas.models import Peliculas


class Sala(models.Model):
    TIPO_SALA_CHOICES = [
            ('IMAX', 'IMAX'),
            ('2D', '2D'),
            ('3D', '3D'),
            ('LASER', 'Láser'),
            ('4DX', '4DX'),
            ('VIP', 'VIP'),
        ]
    identificador = models.CharField("Identificador", max_length=50)
    capacidad = models.IntegerField("Capacidad")
    tiempo_max = models.IntegerField("Tiempo Máximo")
    tipo=models.CharField( "Tipo de sala",choices=TIPO_SALA_CHOICES,null=True,blank=True, )
    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

    def __str__(self):
        return self.identificador

class Sesion(models.Model):
    pelicula = models.ForeignKey(Peliculas, on_delete=models.CASCADE, related_name="sesiones", verbose_name="Película")
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT, related_name="sesiones", verbose_name="Sala")
    horario = models.DateTimeField("Horario de Sesión")

    class Meta:
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"
        ordering = ["horario"]

    def __str__(self):
        return f"{self.pelicula.nombre} en {self.sala.identificador} ({self.horario.strftime('%d/%m/%Y %H:%M')})"

