from django.shortcuts import render
from django.utils import timezone
from peliculas.models import DetallePelicula

def inicio(request):
    return render(request, "core/inicio.html")

def sobrecine(request):
    return render(request, "core/sobrecine.html")

def proximos_estrenos(request):
    # Filtramos las películas que NO están en cartelera y cuya fecha es futura o actual
    estrenos = DetallePelicula.objects.filter(
        en_cartelera=False, 
        fecha_estreno__gte=timezone.now().date()
    ).order_by('fecha_estreno')

    context = {
        'estrenos': estrenos
    }
    # AGREGAR 'core/' ANTES DEL NOMBRE DE LA PLANTILLA
    return render(request, 'core/proximos_estrenos.html', context)