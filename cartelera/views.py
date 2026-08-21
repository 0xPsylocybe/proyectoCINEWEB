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

def detalle_cartelera(request,pk):
    cartelera=get_object_or_404(Peliculas,pk=pk)
    contexto={
        "cartelera":cartelera
    }
    return render (
        request,
        "cartelera/detalle_cartelera.html",
        contexto
    )