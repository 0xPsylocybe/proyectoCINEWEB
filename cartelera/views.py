from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
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
    pelicula = get_object_or_404(
        Peliculas.objects.prefetch_related('sesiones__sala'),
        pk=pk
    )

    fechas_disponibles = pelicula.sesiones.dates('horario', 'day', order='ASC')

    contexto = {
        "pelicula": pelicula,
        "fechas_disponibles": fechas_disponibles,
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
                return redirect('cartelera:lista_sesiones')
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
                return redirect('cartelera:lista_sesiones')
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
        return redirect('cartelera:lista_sesiones')

    contexto = {'sesion': sesion}
    return render(request, 'cartelera/sesion_confirmar_eliminar.html', contexto)