from django.shortcuts import render
from django.utils import timezone
from peliculas.models import DetallePelicula, Peliculas


def inicio(request):
    cartelera = Peliculas.objects.all()
    
    contexto = {
            "cartelera": cartelera
            
        }
    return render(
            request,
            "core/inicio.html",
            contexto
        )

def sobrecine(request):
    return render(request, "core/sobrecine.html")

def proximos_estrenos(request):
    # Todo lo que no está en cartelera, mejor valorado primero.
    # Mismo criterio que la sección "Próximos estrenos" de la cartelera.
    estrenos = (DetallePelicula.objects
                .filter(en_cartelera=False)
                .select_related('pelicula')
                .order_by('-pelicula__puntuacion', 'pelicula__titulo'))

    context = {
        'estrenos': estrenos
    }
    # AGREGAR 'core/' ANTES DEL NOMBRE DE LA PLANTILLA
    return render(request, 'core/proximos_estrenos.html', context)