from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Q
from usuarios.decorators import gestor_required
from peliculas.models import Peliculas
from .models import Sala, Sesion
from .forms import SesionForm

def lista_cartelera(request):
    """Cartelera en dos bloques: lo que se puede ver ya y lo que está por llegar."""

    cartelera = (Peliculas.objects
                 .filter(detalles__en_cartelera=True)
                 .select_related("detalles")
                 .order_by("titulo"))

    # Próximos estrenos: todo lo que no está en cartelera, mejor valorado primero
    proximos = (Peliculas.objects
                .filter(detalles__en_cartelera=False)
                .select_related("detalles")
                .order_by("-puntuacion", "titulo"))

    contexto = {
        "cartelera": cartelera,
        "proximos": proximos,
    }
    return render(
        request,
        "cartelera/cartelera.html",
        contexto
    )

def detalle_cartelera(request, pk):
    from datetime import timedelta, datetime, time

    pelicula = get_object_or_404(
        Peliculas.objects.prefetch_related('sesiones__sala'),
        pk=pk
    )

    # Obtener fecha seleccionada de la URL
    fecha_param = request.GET.get('fecha')

    # Todas las sesiones ordenadas por sala primero, luego por horario
    todas_sesiones = pelicula.sesiones.select_related('sala').order_by('sala', 'horario')

    # Obtener fechas disponibles (para el selector de días)
    fechas_disponibles = pelicula.sesiones.dates('horario', 'day', order='ASC')

    # Obtener fecha seleccionada
    if fecha_param:
        try:
            fecha_selected = datetime.strptime(fecha_param, '%Y-%m-%d').date()
        except:
            fecha_selected = fechas_disponibles[0] if fechas_disponibles else None
    else:
        fecha_selected = fechas_disponibles[0] if fechas_disponibles else None

    # Filtrar sesiones del día seleccionado (12:00 a 02:59 del día siguiente)
    if fecha_selected:
        sesiones_lista = list(todas_sesiones)
        sesiones_filtradas = [
            s for s in sesiones_lista
            if (s.horario.date() == fecha_selected and s.horario.hour >= 12) or
               (s.horario.date() == fecha_selected + timedelta(days=1) and s.horario.hour < 3)
        ]
    else:
        sesiones_filtradas = list(todas_sesiones)

    # Agrupar sesiones por sala en un diccionario
    from collections import defaultdict
    salas_dict = defaultdict(list)
    for sesion in sesiones_filtradas:
        salas_dict[sesion.sala].append(sesion)

    contexto = {
        "pelicula": pelicula,
        "fechas_disponibles": fechas_disponibles,
        "salas_con_sesiones": salas_dict.items(),
    }
    return render(
        request,
        "cartelera/detalle_cartelera.html",
        contexto
    )


# CRUD Sesiones (solo para gestores)

@gestor_required
def lista_sesiones(request):
    """Listado de sesiones para el gestor, con filtros y paginación.

    Son varios cientos de sesiones: sin filtrar, la pantalla es inmanejable.
    """
    from datetime import datetime

    from django.core.paginator import Paginator

    sesiones = Sesion.objects.select_related('pelicula', 'sala').order_by('horario')

    # --- Filtros ---
    pelicula_id = request.GET.get('pelicula') or ''
    if pelicula_id:
        sesiones = sesiones.filter(pelicula_id=pelicula_id)

    sala_id = request.GET.get('sala') or ''
    if sala_id:
        sesiones = sesiones.filter(sala_id=sala_id)

    def leer_fecha(nombre):
        valor = request.GET.get(nombre) or ''
        try:
            return valor, datetime.strptime(valor, '%Y-%m-%d').date()
        except ValueError:
            return valor, None

    desde_txt, desde = leer_fecha('desde')
    hasta_txt, hasta = leer_fecha('hasta')
    if desde:
        sesiones = sesiones.filter(horario__date__gte=desde)
    if hasta:
        sesiones = sesiones.filter(horario__date__lte=hasta)

    total = sesiones.count()

    paginas = Paginator(sesiones, 24)
    pagina = paginas.get_page(request.GET.get('pagina'))

    # Para conservar los filtros al cambiar de página
    filtros = request.GET.copy()
    filtros.pop('pagina', None)

    contexto = {
        'sesiones': pagina,
        'pagina': pagina,
        'total': total,
        'peliculas': Peliculas.objects.filter(sesiones__isnull=False)
                                      .distinct().order_by('titulo'),
        'salas': Sala.objects.order_by('identificador'),
        'filtro_pelicula': pelicula_id,
        'filtro_sala': sala_id,
        'filtro_desde': desde_txt,
        'filtro_hasta': hasta_txt,
        'hay_filtros': any([pelicula_id, sala_id, desde_txt, hasta_txt]),
        'querystring': filtros.urlencode(),
    }
    return render(request, 'cartelera/sesiones_lista.html', contexto)


@gestor_required
def crear_sesion(request):
    if request.method == 'POST':
        form = SesionForm(request.POST)
        if form.is_valid():
            try:
                sesion = form.save(commit=False)
                sesion.full_clean()
                sesion.save()
                messages.success(request, 'Sesión creada exitosamente.')
                return redirect('sesiones_lista')
            except Exception as e:
                messages.error(request, f'Error al crear la sesión: {str(e)}')
    else:
        form = SesionForm()

    contexto = {'form': form, 'titulo': 'Nueva Sesión'}
    return render(request, 'cartelera/sesion_form.html', contexto)


@gestor_required
def editar_sesion(request, pk):
    sesion = get_object_or_404(Sesion, pk=pk)

    if request.method == 'POST':
        form = SesionForm(request.POST, instance=sesion)
        if form.is_valid():
            try:
                form_sesion = form.save(commit=False)
                form_sesion.full_clean()
                form_sesion.save()
                messages.success(request, 'Sesión actualizada exitosamente.')
                return redirect('sesiones_lista')
            except Exception as e:
                messages.error(request, f'Error al actualizar la sesión: {str(e)}')
    else:
        form = SesionForm(instance=sesion)

    contexto = {'form': form, 'sesion': sesion, 'titulo': 'Editar Sesión'}
    return render(request, 'cartelera/sesion_form.html', contexto)


@gestor_required
def eliminar_sesion(request, pk):
    sesion = get_object_or_404(Sesion, pk=pk)

    if request.method == 'POST':
        sesion.delete()
        messages.success(request, 'Sesión eliminada exitosamente.')
        return redirect('sesiones_lista')

    contexto = {'sesion': sesion}
    return render(request, 'cartelera/sesion_confirmar_eliminar.html', contexto)


@gestor_required
def rellenar_sesiones(request):
    from datetime import timedelta, datetime
    from .forms import RellenarSesionesForm

    if request.method == 'POST':
        form = RellenarSesionesForm(request.POST)
        if form.is_valid():
            peliculas = form.cleaned_data['peliculas']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            salas = form.cleaned_data['salas']
            borrar_existentes = form.cleaned_data['borrar_existentes']

            from collections import defaultdict

            from django.db import transaction

            from cartelera import programacion

            peliculas = list(peliculas)
            salas = list(salas)
            dias = (fecha_fin - fecha_inicio).days + 1

            with transaction.atomic():
                if borrar_existentes:
                    # Las sesiones con entradas vendidas no se pueden borrar
                    # (VentaEntrada.sesion es PROTECT) ni se debe: la venta manda.
                    conservadas = Sesion.objects.filter(
                        pelicula__in=peliculas, entradas_vendidas__isnull=False)
                    a_borrar = (Sesion.objects.filter(pelicula__in=peliculas)
                                .exclude(pk__in=conservadas.values("pk")))
                    cuantas = conservadas.count()
                    a_borrar.delete()
                    if cuantas:
                        messages.warning(
                            request,
                            '%d sesiones se han conservado porque tienen entradas '
                            'vendidas.' % cuantas)

                # Se respeta lo que ya haya programado en esas salas
                ocupacion = defaultdict(list)
                for sesion in Sesion.objects.filter(sala__in=salas).select_related(
                        "pelicula", "sala"):
                    ocupacion[sesion.sala_id].append(
                        (sesion.horario, sesion.hora_fin_limpieza))

                nuevas, descartes = programacion.generar(
                    peliculas, salas, dias, fecha_inicio, ocupacion)
                Sesion.objects.bulk_create(nuevas, batch_size=500)

            messages.success(
                request, '✓ %d sesiones generadas correctamente.' % len(nuevas))
            if descartes["sala_ocupada"]:
                messages.info(
                    request,
                    '%d pases no se pudieron programar porque la sala seguía '
                    'ocupada por la sesión anterior.' % descartes["sala_ocupada"])
            return redirect('sesiones_lista')
    else:
        form = RellenarSesionesForm()

    contexto = {'form': form}
    return render(request, 'cartelera/rellenar_sesiones.html', contexto)