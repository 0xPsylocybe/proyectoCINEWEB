from django.shortcuts import get_object_or_404, redirect, render
from .forms import PeliculasForm
from .models import Peliculas


def crear_pelicula(request):
    if request.method == "POST":
        formulario = PeliculasForm(request.POST, request.FILES)

        if formulario.is_valid():
            formulario.save()
            return redirect("lista_peliculas")
    else:
        formulario = PeliculasForm()

    return render(request, "peliculas/nueva_pelicula.html", {"formulario": formulario})


def lista_peliculas(request):
    peliculas = Peliculas.objects.all()

    contexto = {"peliculas": peliculas}

    return render(request, "peliculas/lista_peliculas.html", contexto)


def editar_peliculas(request, pk):
    pelicula = get_object_or_404(Peliculas, pk=pk)

    if request.method == "POST":
        formulario = PeliculasForm(request.POST, request.FILES, instance=pelicula)

        if formulario.is_valid():
            formulario.save()
            return redirect("lista_peliculas")
    else:
        formulario = PeliculasForm(instance=pelicula)

    return render(request, "peliculas/nueva_pelicula.html", {"formulario": formulario})


def eliminar_pelicula(request, pk):
    pelicula = get_object_or_404(Peliculas, pk=pk)

    if request.method == "POST":
        pelicula.delete()
        return redirect("lista_peliculas")

    return render(
        request,
        "peliculas/eliminar_pelicula.html",  
        {"pelicula": pelicula},
    )

def detalle_pelicula(request,pk):
    pelicula=get_object_or_404(Peliculas,pk=pk)
    contexto={
        "pelicula":pelicula
    }
    return render (
        request,
        "peliculas/detalle_pelicula.html",
        contexto
    )