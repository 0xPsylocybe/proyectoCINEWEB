from django.db import models
from peliculas.models import Peliculas

class CaracteristicaSala(models.Model):
    nombre = models.CharField(max_length=80)

    class Meta:
        verbose_name = "Característica de sala"
        verbose_name_plural = "Características de sala"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class Sala(models.Model):
    identificador = models.CharField("Identificador", max_length=50)
    capacidad = models.IntegerField("Capacidad")
    tiempo_max = models.IntegerField("Tiempo Máximo")
    caracteristicas = models.ManyToManyField(CaracteristicaSala, related_name="salas")

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


class Sesion(models.Model):
    pelicula = models.ForeignKey("peliculas.Pelicula",on_delete=models.CASCADE,related_name="sesiones",)
    sala = models.ForeignKey(Sala,on_delete=models.PROTECT,related_name="sesiones",)

    class Meta:
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"

    def __str__(self):
        return f"{self.pelicula} en {self.sala}"
