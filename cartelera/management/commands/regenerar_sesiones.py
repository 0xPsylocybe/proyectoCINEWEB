from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from peliculas.models import Peliculas
from cartelera.models import Sala, Sesion
import random


class Command(BaseCommand):
    help = 'Regenera todas las sesiones basadas en películas en cartelera'

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=14, help='Número de días a generar sesiones (default: 14)')
        parser.add_argument('--borrar', action='store_true', help='Borrar sesiones existentes antes de regenerar')

    def handle(self, *args, **options):
        dias = options['dias']
        borrar = options['borrar']

        if borrar:
            Sesion.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Sesiones anteriores eliminadas'))

        # Horarios por día de la semana
        horarios_por_dia = {
            0: [18, 20, 22],  # Lunes
            1: [18, 20, 22],  # Martes
            2: [18, 20, 22],  # Miércoles
            3: [18, 20, 22],  # Jueves
            4: [18, 20, 22, 0],  # Viernes
            5: [12, 18, 20, 22, 0],  # Sábado
            6: [12, 14, 18, 20, 22, 0],  # Domingo
        }

        base_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        salas = list(Sala.objects.all())
        peliculas_cartelera = list(Peliculas.objects.filter(detalles__en_cartelera=True))

        if not salas:
            self.stdout.write(self.style.ERROR('✗ No hay salas creadas'))
            return

        if not peliculas_cartelera:
            self.stdout.write(self.style.ERROR('✗ No hay películas en cartelera'))
            return

        sesiones_creadas = 0

        for pelicula_idx, pelicula in enumerate(peliculas_cartelera):
            # Asignar 3-4 salas por película
            num_salas = min(4, len(salas))
            salas_asignadas = []
            for i in range(num_salas):
                sala_idx = (pelicula_idx * num_salas + i) % len(salas)
                salas_asignadas.append(salas[sala_idx])

            for dia_offset in range(dias):
                fecha = base_time + timedelta(days=dia_offset)
                dia_semana = fecha.weekday()
                horas = horarios_por_dia[dia_semana]

                for hora in horas:
                    sala = salas_asignadas[hora % len(salas_asignadas)]

                    if hora == 0:
                        horario = fecha + timedelta(days=1, hours=0, minutes=random.randint(0, 30))
                    else:
                        horario = fecha.replace(hour=hora, minute=random.randint(0, 30))

                    try:
                        sesion, created = Sesion.objects.get_or_create(
                            pelicula=pelicula,
                            sala=sala,
                            horario=horario
                        )
                        if created:
                            sesiones_creadas += 1
                    except:
                        pass

        self.stdout.write(self.style.SUCCESS(f'✓ {sesiones_creadas} sesiones generadas'))
        self.stdout.write(f'Total sesiones en BD: {Sesion.objects.count()}')
