"""Disponibilidad y bloqueo temporal de butacas.

Una butaca está ocupada si ya se vendió (EntradaButaca) o si otro comprador
la tiene bloqueada y el bloqueo aún no ha caducado (ReservaButaca).
"""

from django.db import IntegrityError, transaction

from .models import EntradaButaca, ReservaButaca


def etiqueta(fila, numero):
    """(1, 7) -> 'A7'"""
    return f"{chr(ord('A') + fila - 1)}{numero}"


def _clave(request):
    """Identifica al comprador anónimo. Fuerza la creación de la cookie de
    sesión si aún no existe, porque el bloqueo cuelga de ella."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def estado_sesion(sesion, request):
    """Devuelve (vendidas, reservadas_por_otros, mis_reservas) como conjuntos
    de tuplas (fila, numero)."""
    ReservaButaca.limpiar_caducadas()
    clave = _clave(request)

    vendidas = set(
        EntradaButaca.objects.filter(sesion=sesion).values_list("fila", "numero")
    )
    reservas = ReservaButaca.objects.filter(sesion=sesion)
    ajenas = set(reservas.exclude(session_key=clave).values_list("fila", "numero"))
    propias = set(reservas.filter(session_key=clave).values_list("fila", "numero"))
    return vendidas, ajenas, propias


def mapa(sesion, request):
    """Rejilla lista para pintar: cada butaca con su estado."""
    vendidas, ajenas, propias = estado_sesion(sesion, request)
    sala = sesion.sala

    filas = []
    for f in range(1, sala.filas + 1):
        butacas = []
        for n in range(1, sala.columnas + 1):
            if (f, n) in vendidas or (f, n) in ajenas:
                estado = "ocupada"
            elif (f, n) in propias:
                estado = "seleccionada"
            else:
                estado = "libre"
            butacas.append({
                "fila": f,
                "numero": n,
                "etiqueta": etiqueta(f, n),
                "estado": estado,
            })
        filas.append({"letra": chr(ord("A") + f - 1), "butacas": butacas})

    return {
        "filas": filas,
        "columnas": sala.columnas,
        "seleccionadas": sorted(propias),
    }


def reservar(sesion, butacas, request):
    """Bloquea las butacas indicadas durante MINUTOS_RESERVA.

    `butacas` es una lista de tuplas (fila, numero). Sustituye por completo la
    selección previa del comprador para esta sesión.

    Devuelve la lista de butacas que NO se pudieron bloquear porque otro se
    adelantó (vacía si fue todo bien).
    """
    ReservaButaca.limpiar_caducadas()
    clave = _clave(request)
    expira = ReservaButaca.nueva_expiracion()

    vendidas = set(
        EntradaButaca.objects.filter(sesion=sesion).values_list("fila", "numero")
    )

    # La selección anterior se descarta: el usuario acaba de elegir otra.
    ReservaButaca.objects.filter(sesion=sesion, session_key=clave).delete()

    conflictos = []
    for fila, numero in butacas:
        if (fila, numero) in vendidas:
            conflictos.append(etiqueta(fila, numero))
            continue
        try:
            # atomic por butaca: un choque no invalida el resto de la selección.
            with transaction.atomic():
                ReservaButaca.objects.create(
                    sesion=sesion,
                    fila=fila,
                    numero=numero,
                    session_key=clave,
                    expira_en=expira,
                )
        except IntegrityError:
            # Otro comprador la bloqueó entre la comprobación y el insert.
            conflictos.append(etiqueta(fila, numero))

    return conflictos


def mis_reservas(sesion, request):
    """Bloqueos vigentes del comprador para esta sesión."""
    ReservaButaca.limpiar_caducadas()
    return list(
        ReservaButaca.objects.filter(sesion=sesion, session_key=_clave(request))
    )


def confirmar(venta, sesion, request):
    """Convierte los bloqueos vigentes en butacas vendidas.

    Devuelve la lista de butacas perdidas: las que caducaron y otro compró
    mientras tanto. Si no está vacía, la venta no es válida tal cual.
    """
    clave = _clave(request)
    reservas = list(
        ReservaButaca.objects.filter(sesion=sesion, session_key=clave)
    )

    perdidas = []
    for reserva in reservas:
        try:
            with transaction.atomic():
                EntradaButaca.objects.create(
                    venta=venta,
                    sesion=sesion,
                    fila=reserva.fila,
                    numero=reserva.numero,
                )
        except IntegrityError:
            perdidas.append(reserva.etiqueta)

    ReservaButaca.objects.filter(sesion=sesion, session_key=clave).delete()
    return perdidas
