from django.db import models
from peliculas.models import Peliculas

class CaracteristicasSala(models.Model):
    nombre = models.CharField("Nombre", max_length=100)
    descripcion = models.CharField("Descripcion", max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Característica de Sala"
        verbose_name_plural = "Características de Sala"

    def __str__(self):
        return self.nombre

class Sala(models.Model):
    identificador = models.CharField("Identificador", max_length=50)
    capacidad = models.IntegerField("Capacidad")
    tiempo_max = models.IntegerField("Tiempo Máximo")
    caracteristicas = models.ManyToManyField(CaracteristicasSala, related_name="salas")

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

    def __str__(self):
        return self.identificador

class PeliculasEnSala(models.Model):
    pelicula = models.ForeignKey(Peliculas, on_delete=models.CASCADE, related_name="peliculas_en_sala")
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name="peliculas_en_sala")
    horario = models.DateTimeField("Horario de Sesión")

    class Meta:
        verbose_name = "Película en Sala (Sesión)"
        verbose_name_plural = "Películas en Sala (Sesiones)"

    def __str__(self):
        return f"{self.pelicula.nombre} en {self.sala.identificador} ({self.horario})"