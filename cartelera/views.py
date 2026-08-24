from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Q
from usuarios.decorators import gestor_required
from peliculas.models import Peliculas
from .models import Sesion
from .forms import SesionForm

def lista_cartelera(request):
    cartelera = Peliculas.objects.all()
    contexto = {
        "cartelera": cartelera
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
    sesiones = Sesion.objects.select_related('pelicula', 'sala').order_by('horario')
    contexto = {'sesiones': sesiones}
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

            # Borrar sesiones existentes si lo solicita
            if borrar_existentes:
                Sesion.objects.filter(pelicula__in=peliculas).delete()

            # Horarios por día de la semana
            horarios_por_dia = {
                0: [18, 20, 22],
                1: [18, 20, 22],
                2: [18, 20, 22],
                3: [18, 20, 22],
                4: [18, 20, 22, 0],
                5: [12, 18, 20, 22, 0],
                6: [12, 14, 18, 20, 22, 0],
            }

            sesiones_creadas = 0
            fecha_actual = fecha_inicio

            while fecha_actual <= fecha_fin:
                dia_semana = fecha_actual.weekday()
                horas = horarios_por_dia.get(dia_semana, [])

                for idx, pelicula in enumerate(peliculas):
                    for hora_idx, hora in enumerate(horas):
                        sala = salas[( idx * len(horas) + hora_idx) % len(salas)]

                        if hora == 0:
                            horario = fecha_actual + timedelta(days=1, hours=0, minutes=0)
                        else:
                            horario = fecha_actual.replace(hour=hora, minute=0)

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

                fecha_actual += timedelta(days=1)

            messages.success(request, f'✓ {sesiones_creadas} sesiones generadas correctamente.')
            return redirect('sesiones_lista')
    else:
        form = RellenarSesionesForm()

    contexto = {'form': form}
    return render(request, 'cartelera/rellenar_sesiones.html', contexto)