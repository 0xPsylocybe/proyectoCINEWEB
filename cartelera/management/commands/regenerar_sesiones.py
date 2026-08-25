"""Regenera la programación de sesiones de las películas en cartelera.

Las reglas (horas de pase, madrugadas, duración máxima del último pase) están
en `cartelera/programacion.py`, compartidas con la vista "Rellenar
automáticamente" para que las dos generen lo mismo.

Uso:
    python manage.py regenerar_sesiones --dry-run          # ensayo, no toca nada
    python manage.py regenerar_sesiones --dias 14 --borrar
"""

from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from cartelera import programacion
from cartelera.models import Sala, Sesion
from peliculas.models import Peliculas


class Command(BaseCommand):
    """Regenera la programacion respetando la ocupacion de cada sala."""
    help = "Regenera las sesiones de las películas en cartelera"

    def add_arguments(self, parser):
        """Configura los argumentos de línea de comandos para la regeneración de sesiones."""
        parser.add_argument("--dias", type=int, default=14,
                            help="Días a programar (por defecto 14)")
        parser.add_argument("--borrar", action="store_true",
                            help="Borra las sesiones existentes antes de regenerar")
        parser.add_argument("--dry-run", action="store_true",
                            help="Muestra lo que haría sin guardar nada")

    def handle(self, *args, **opciones):
        """Ejecuta el algoritmo de programación automática y guarda las sesiones en base de datos."""
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

        # Las sesiones con entradas vendidas no se tocan: la venta manda, y
        # además la BBDD lo impide (VentaEntrada.sesion es PROTECT).
        vendidas = list(Sesion.objects.filter(entradas_vendidas__isnull=False)
                        .select_related("pelicula", "sala").distinct())

        # Hay que respetar la ocupación de lo que se conserva
        ocupacion_previa = defaultdict(list)
        intactas = vendidas if borrar else list(
            Sesion.objects.select_related("pelicula", "sala"))
        for sesion in intactas:
            ocupacion_previa[sesion.sala_id].append(
                (sesion.horario, sesion.hora_fin_limpieza))

        if borrar and vendidas:
            self.stdout.write(self.style.WARNING(
                "%d sesiones se conservan porque tienen entradas vendidas:" % len(vendidas)))
            for sesion in vendidas[:10]:
                self.stdout.write("   %s" % sesion)

        # localdate y no now(): las horas de la tabla son horas locales
        nuevas, descartes = programacion.generar(
            peliculas, salas, dias, timezone.localdate(), ocupacion_previa)

        if not ensayo:
            # Borrado e inserción juntos: así la cartelera nunca se queda vacía
            # a ojos de quien esté navegando.
            with transaction.atomic():
                if borrar:
                    # Solo las que nadie ha comprado
                    borradas = (Sesion.objects
                                .exclude(pk__in=[s.pk for s in vendidas])
                                .delete()[0])
                    self.stdout.write("Sesiones anteriores eliminadas: %d" % borradas)
                Sesion.objects.bulk_create(nuevas, batch_size=500)

        self._resumen(nuevas, descartes, peliculas, dias, ensayo)

    def _resumen(self, nuevas, descartes, peliculas, dias, ensayo):
        """Imprime en consola las estadísticas y reparto de sesiones generadas."""
        self.stdout.write("")
        verbo = "Se crearían" if ensayo else "Creadas"
        self.stdout.write(self.style.SUCCESS("%s %d sesiones en %d días"
                                             % (verbo, len(nuevas), dias)))

        if descartes["sala_ocupada"]:
            self.stdout.write(self.style.WARNING(
                "%d huecos sin cubrir: la sala seguía ocupada por el pase anterior"
                % descartes["sala_ocupada"]))
        if descartes["sin_pelicula_corta"]:
            self.stdout.write(self.style.WARNING(
                "%d huecos de madrugada sin cubrir: no hay películas de menos de %s"
                % (descartes["sin_pelicula_corta"],
                   programacion.DURACION_MAXIMA_MADRUGADA)))

        por_pelicula = defaultdict(set)
        pases = defaultdict(int)
        madrugadas = defaultdict(int)
        for sesion in nuevas:
            por_pelicula[sesion.pelicula.titulo].add(sesion.sala.identificador)
            pases[sesion.pelicula.titulo] += 1
            if programacion.es_madrugada(timezone.localtime(sesion.horario).hour):
                madrugadas[sesion.pelicula.titulo] += 1

        sin_programar = [p.titulo for p in peliculas if p.titulo not in por_pelicula]

        self.stdout.write("")
        self.stdout.write("Reparto por película:")
        for titulo in sorted(por_pelicula):
            extra = ("  (%d de madrugada)" % madrugadas[titulo]) if madrugadas[titulo] else ""
            self.stdout.write("   %-42s %3d pases en %d salas%s"
                              % (titulo[:42], pases[titulo],
                                 len(por_pelicula[titulo]), extra))

        if sin_programar:
            self.stdout.write(self.style.ERROR(
                "\nSin ningún pase: %s" % ", ".join(sin_programar)))

        if not ensayo:
            self.stdout.write("")
            self.stdout.write("Total de sesiones en la BBDD: %d" % Sesion.objects.count())
