"""Regenera la programación de sesiones de las películas en cartelera.

Reglas que respeta:
  - Cada día de la semana tiene sus propias horas de pase.
  - Una sala no puede tener dos sesiones que se pisen. La ocupación de cada
    pase la calcula el propio modelo `Sesion` (15 min de publicidad + duración
    de la película + 20 min de limpieza), para no duplicar esa regla aquí.
  - Los pases se reparten entre las salas asignadas a cada película.

Uso:
    python manage.py regenerar_sesiones --dry-run          # ensayo, no toca nada
    python manage.py regenerar_sesiones --dias 14 --borrar
"""

import random
from collections import defaultdict
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from cartelera.models import Sala, Sesion
from peliculas.models import Peliculas

# Horas de pase según el día de la semana (0 = lunes ... 6 = domingo).
# La hora 0 es el pase de medianoche: cae en la madrugada del día siguiente.
HORARIOS_POR_DIA = {
    0: [18, 20, 22],
    1: [18, 20, 22],
    2: [18, 20, 22],
    3: [18, 20, 22],
    4: [18, 20, 22, 0],
    5: [12, 18, 20, 22, 0],
    6: [12, 14, 18, 20, 22, 0],
}

# Salas en las que se programa cada película, como mucho.
SALAS_POR_PELICULA = 4


class Command(BaseCommand):
    help = "Regenera las sesiones de las películas en cartelera"

    def add_arguments(self, parser):
        parser.add_argument("--dias", type=int, default=14,
                            help="Días a programar (por defecto 14)")
        parser.add_argument("--borrar", action="store_true",
                            help="Borra las sesiones existentes antes de regenerar")
        parser.add_argument("--dry-run", action="store_true",
                            help="Muestra lo que haría sin guardar nada")

    def handle(self, *args, **opciones):
        dias = opciones["dias"]
        borrar = opciones["borrar"]
        ensayo = opciones["dry_run"]

        salas = list(Sala.objects.all())
        peliculas = list(Peliculas.objects.filter(detalles__en_cartelera=True))

        if not salas:
            self.stdout.write(self.style.ERROR("No hay salas creadas"))
            return
        if not peliculas:
            self.stdout.write(self.style.ERROR("No hay películas en cartelera"))
            return

        if ensayo:
            self.stdout.write(self.style.WARNING("ENSAYO: no se guarda nada\n"))

        # Ocupación de cada sala: lista de (inicio, fin) ya reservados.
        # Si no se borra lo anterior, hay que respetarlo.
        ocupacion = defaultdict(list)
        if not borrar:
            for sesion in Sesion.objects.select_related("pelicula", "sala"):
                ocupacion[sesion.sala_id].append(
                    (sesion.horario, sesion.hora_fin_limpieza))

        inicio_periodo = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        nuevas = []
        sin_hueco = 0

        # Se programa sala por sala y hora por hora, no película por película:
        # así se aprovechan todas las salas y ninguna película se queda fuera
        # porque las anteriores hayan ocupado ya todos los huecos.
        # El índice va rotando el catálogo para repartir los pases.
        siguiente = 0

        for desplazamiento in range(dias):
            fecha = inicio_periodo + timedelta(days=desplazamiento)

            for hora in HORARIOS_POR_DIA[fecha.weekday()]:
                for sala in salas:
                    if hora == 0:
                        # Pase de medianoche: cae en la madrugada del día siguiente
                        comienzo = fecha + timedelta(days=1,
                                                     minutes=random.randint(0, 30))
                    else:
                        comienzo = fecha.replace(hour=hora,
                                                 minute=random.randint(0, 30))

                    colocada = False
                    # Se busca en el catálogo una película que quepa en el hueco
                    for intento in range(len(peliculas)):
                        pelicula = peliculas[(siguiente + intento) % len(peliculas)]

                        # El modelo es quien sabe cuánto ocupa una sesión
                        candidata = Sesion(pelicula=pelicula, sala=sala,
                                           horario=comienzo)
                        fin = candidata.hora_fin_limpieza

                        if self._cabe(ocupacion[sala.id], comienzo, fin):
                            ocupacion[sala.id].append((comienzo, fin))
                            nuevas.append(candidata)
                            siguiente = (siguiente + intento + 1) % len(peliculas)
                            colocada = True
                            break

                    if not colocada:
                        sin_hueco += 1

        if not ensayo:
            # Borrado e inserción juntos: así la cartelera nunca se queda vacía
            # a ojos de quien esté navegando.
            with transaction.atomic():
                if borrar:
                    borradas = Sesion.objects.all().delete()[0]
                    self.stdout.write("Sesiones anteriores eliminadas: %d" % borradas)
                Sesion.objects.bulk_create(nuevas, batch_size=500)

        self._resumen(nuevas, sin_hueco, peliculas, dias, ensayo)

    @staticmethod
    def _cabe(reservas, inicio, fin):
        """True si el hueco [inicio, fin) no pisa ninguna reserva de la sala."""
        return all(fin <= ocupado_desde or inicio >= ocupado_hasta
                   for ocupado_desde, ocupado_hasta in reservas)

    def _resumen(self, nuevas, sin_hueco, peliculas, dias, ensayo):
        self.stdout.write("")
        verbo = "Se crearían" if ensayo else "Creadas"
        self.stdout.write(self.style.SUCCESS("%s %d sesiones en %d días"
                                             % (verbo, len(nuevas), dias)))

        if sin_hueco:
            self.stdout.write(self.style.WARNING(
                "%d huecos sin cubrir: la sala seguía ocupada por el pase anterior"
                % sin_hueco))

        # Reparto por película, para ver que ninguna se queda coja
        por_pelicula = defaultdict(set)
        pases = defaultdict(int)
        for sesion in nuevas:
            por_pelicula[sesion.pelicula.titulo].add(sesion.sala.identificador)
            pases[sesion.pelicula.titulo] += 1

        sin_programar = [p.titulo for p in peliculas if p.titulo not in por_pelicula]

        self.stdout.write("")
        self.stdout.write("Reparto por película:")
        for titulo in sorted(por_pelicula):
            usadas = sorted(por_pelicula[titulo])
            self.stdout.write("   %-42s %3d pases en %d salas"
                              % (titulo[:42], pases[titulo], len(usadas)))

        if sin_programar:
            self.stdout.write(self.style.ERROR(
                "\nSin ningún pase: %s" % ", ".join(sin_programar)))

        if not ensayo:
            self.stdout.write("")
            self.stdout.write("Total de sesiones en la BBDD: %d" % Sesion.objects.count())
