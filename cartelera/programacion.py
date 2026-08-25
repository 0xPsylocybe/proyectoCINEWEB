"""Reglas de programación de la cartelera.

Lo usan el comando `regenerar_sesiones` y la vista "Rellenar automáticamente",
para que las dos generen la misma programación en vez de tener cada una su
propia tabla de horarios.
"""

from collections import defaultdict
from datetime import datetime, time, timedelta

from django.utils import timezone

from cartelera.models import Sesion

# Horas de pase por día de la semana (0 = lunes ... 6 = domingo), como
# pares (hora, minuto).
#
#   - De lunes a viernes no se abre antes de las 17:00.
#   - Sábado y domingo hay matinal.
#   - Viernes y sábado el último pase es a la 1:00 (madrugada del día siguiente).
#   - Los saltos son de 2h30 en vez de 2h: con pases cada dos horas solo caben
#     películas de hasta 85 minutos, contando publicidad y limpieza.
HORARIOS_POR_DIA = {
    0: [(17, 0), (19, 30), (22, 0)],                          # lunes
    1: [(17, 0), (19, 30), (22, 0)],                          # martes
    2: [(17, 0), (19, 30), (22, 0)],                          # miércoles
    3: [(17, 0), (19, 30), (22, 0)],                          # jueves
    4: [(17, 0), (19, 30), (22, 0), (1, 0)],                  # viernes
    5: [(12, 0), (14, 30), (17, 0), (19, 30), (22, 0), (1, 0)],   # sábado
    6: [(12, 0), (14, 30), (17, 0), (19, 30), (22, 0)],       # domingo
}

# Un pase que empiece antes de esta hora pertenece a la noche del día anterior
# (el "día de cine" va de las 12:00 a las 02:59).
FIN_DE_LA_MADRUGADA = 6

# En el pase de madrugada no se programan películas largas.
DURACION_MAXIMA_MADRUGADA = timedelta(hours=2)

DURACION_POR_DEFECTO = timedelta(minutes=120)


def es_madrugada(hora):
    return hora < FIN_DE_LA_MADRUGADA


def duracion(pelicula):
    return pelicula.duracion or DURACION_POR_DEFECTO


def cabe_en_la_franja(pelicula, hora):
    """El último pase de la noche no admite películas de más de dos horas."""
    if es_madrugada(hora):
        return duracion(pelicula) <= DURACION_MAXIMA_MADRUGADA
    return True


def momento_del_pase(dia, hora, minuto):
    """Convierte una franja en un datetime, en hora local.

    `dia` es un `date`. Las franjas de madrugada caen en el día siguiente: el
    pase de la 1:00 del viernes se proyecta de hecho la madrugada del sábado.

    Ojo: hay que construirlo con `make_aware` sobre la hora local. Si se usa
    `timezone.now().replace(hour=17)` se obtienen las 17:00 **UTC**, que en
    Madrid son las 19:00: la programación entera queda corrida dos horas.
    """
    if es_madrugada(hora):
        dia = dia + timedelta(days=1)
    return timezone.make_aware(datetime.combine(dia, time(hora, minuto)))


def _libre(reservas, inicio, fin):
    """True si el hueco [inicio, fin) no pisa ninguna reserva de la sala."""
    return all(fin <= ocupado_desde or inicio >= ocupado_hasta
               for ocupado_desde, ocupado_hasta in reservas)


def generar(peliculas, salas, dias, desde, ocupacion_previa=None):
    """Devuelve (sesiones_a_crear, descartes). `desde` es un `date`.

    Recorre día → hora → sala y busca para cada hueco una película que quepa,
    en lugar de ir película por película: así se aprovechan todas las salas y
    ninguna película se queda fuera porque las anteriores hayan ocupado ya
    todos los huecos.

    `descartes` cuenta por qué no se pudo cubrir cada hueco.
    """
    ocupacion = defaultdict(list)
    for sala_id, tramos in (ocupacion_previa or {}).items():
        ocupacion[sala_id].extend(tramos)

    sesiones = []
    descartes = {"sala_ocupada": 0, "sin_pelicula_corta": 0}
    siguiente = 0

    for desplazamiento in range(dias):
        dia = desde + timedelta(days=desplazamiento)

        for hora, minuto in HORARIOS_POR_DIA[dia.weekday()]:
            comienzo = momento_del_pase(dia, hora, minuto)

            # Para la franja de madrugada solo se consideran las cortas
            candidatas = [p for p in peliculas if cabe_en_la_franja(p, hora)]
            if not candidatas:
                descartes["sin_pelicula_corta"] += len(salas)
                continue

            for sala in salas:
                colocada = False

                for intento in range(len(candidatas)):
                    pelicula = candidatas[(siguiente + intento) % len(candidatas)]

                    # El modelo es quien sabe cuánto ocupa una sesión
                    # (publicidad + película + limpieza)
                    candidata = Sesion(pelicula=pelicula, sala=sala, horario=comienzo)
                    fin = candidata.hora_fin_limpieza

                    if _libre(ocupacion[sala.id], comienzo, fin):
                        ocupacion[sala.id].append((comienzo, fin))
                        sesiones.append(candidata)
                        siguiente = (siguiente + intento + 1) % len(candidatas)
                        colocada = True
                        break

                if not colocada:
                    descartes["sala_ocupada"] += 1

    return sesiones, descartes
