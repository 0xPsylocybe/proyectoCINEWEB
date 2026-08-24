from django.shortcuts import get_object_or_404, redirect, render
from peliculas.models  import Peliculas

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