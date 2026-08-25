"""Modelos de la cartelera: salas y sesiones, con sus tiempos de ocupacion."""

from django.db import models
from peliculas.models import Peliculas


class Sala(models.Model):
    """Representa una sala de cine, su capacidad, tipo de proyección y dimensiones."""
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
    tipo = models.CharField("Tipo de sala", choices=TIPO_SALA_CHOICES, null=True, blank=True)
    precio_entrada = models.DecimalField("Precio entrada", max_digits=6, decimal_places=2, default=10.00, help_text="Precio base de entrada para esta sala")
    filas = models.PositiveIntegerField("Filas", default=10, help_text="Filas del mapa de butacas")
    columnas = models.PositiveIntegerField("Butacas por fila", default=15)

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

    def __str__(self):
        return self.identificador

class Sesion(models.Model):
    """Representa la proyección de una película en una sala y horario específicos."""
    pelicula = models.ForeignKey(Peliculas, on_delete=models.CASCADE, related_name="sesiones", verbose_name="Película")
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT, related_name="sesiones", verbose_name="Sala")
    horario = models.DateTimeField("Horario de Sesión", help_text="Hora de apertura de sala (15 min antes de película)")

    class Meta:
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"
        ordering = ["horario"]
        constraints = [
            models.UniqueConstraint(fields=['sala', 'horario'], name='unica_sesion_por_sala_hora')
        ]

    def __str__(self):
        return f"{self.pelicula.titulo} en {self.sala.identificador} ({self.horario.strftime('%d/%m/%Y %H:%M')})"

    # Tiempos de la sesión (Opción B: horario = inicio real de sala)
    @property
    def hora_inicio_publicidad(self):
        """Hora de apertura de la sala e inicio de anuncios publicitarios."""
        return self.horario

    @property
    def hora_inicio_pelicula(self):
        """Hora de inicio real de la película (15 minutos tras la apertura)."""
        from datetime import timedelta
        return self.horario + timedelta(minutes=15)

    @property
    def hora_fin_pelicula(self):
        """Hora en la que finaliza la proyección de la película."""
        from datetime import timedelta
        # duracion es un DurationField, convertir a minutos
        if self.pelicula.duracion:
            duracion_min = int(self.pelicula.duracion.total_seconds() / 60)
        else:
            duracion_min = 120
        return self.hora_inicio_pelicula + timedelta(minutes=duracion_min)

    @property
    def hora_fin_limpieza(self):
        """Hora en la que concluyen las labores de limpieza (20 minutos tras la película)."""
        from datetime import timedelta
        return self.hora_fin_pelicula + timedelta(minutes=20)

    @property
    def duracion_total_ocupacion(self):
        """Tiempo total que la sala estará ocupada (publicidad + película + limpieza)"""
        return (self.hora_fin_limpieza - self.horario).total_seconds() / 60

    def clean(self):
        """Validar que no haya solapamientos en la sala"""
        from django.core.exceptions import ValidationError
        from datetime import timedelta

        if not self.sala or not self.horario:
            return

        # Calcular hora de fin de limpieza para esta sesión
        hora_fin = self.hora_fin_limpieza

        # Buscar sesiones que se solapen en la misma sala
        # Se solapa si: horario < hora_fin AND hora_fin_de_otra > horario
        sesiones_solapadas = Sesion.objects.filter(
            sala=self.sala
        ).exclude(pk=self.pk if self.pk else -1)

        for sesion in sesiones_solapadas:
            # Verificar solapamiento
            if sesion.horario < hora_fin and sesion.hora_fin_limpieza > self.horario:
                raise ValidationError(
                    f"Hay un solapamiento con otra sesión en la sala. "
                    f"La sala estará ocupada hasta {hora_fin.strftime('%H:%M')}"
                )

