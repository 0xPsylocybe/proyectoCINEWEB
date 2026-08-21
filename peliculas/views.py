from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .forms import PeliculasForm, GeneroForm,DirectorForm
from .models import Peliculas,Director,Genero


def crear_pelicula(request):
    if request.method == "POST":
        formulario = PeliculasForm(request.POST, request.FILES)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "¡Película creada correctamente!")
            return redirect("lista_peliculas")
    else:
        formulario = PeliculasForm()

    return render(request, "peliculas/nueva_pelicula.html", {"formulario": formulario})


def lista_peliculas(request):
    if request.method == 'POST' and 'guardar_genero' in request.POST:
        genero_form = GeneroForm(request.POST)
        if genero_form.is_valid():
            genero_form.save()
            messages.success(request, "¡Género creado correctamente!")  # <-- Mensaje de éxito
            return redirect('lista_peliculas')
    
    elif request.method == 'POST' and 'guardar_director' in request.POST:
        director_form = DirectorForm(request.POST)
        if director_form.is_valid():
            director_form.save()
            messages.success(request, "¡Director creado correctamente!")  # <-- Mensaje de éxito
            return redirect('lista_peliculas')

    peliculas = Peliculas.objects.all()
    genero_form = GeneroForm()
    director_form = DirectorForm()

    contexto = {
        "peliculas": peliculas,
        "genero_form": genero_form,
        "director_form": director_form,
    }

    return render(request, "peliculas/lista_peliculas.html", contexto)


def editar_peliculas(request, pk):
    pelicula = get_object_or_404(Peliculas, pk=pk)

    if request.method == "POST":
        formulario = PeliculasForm(request.POST, request.FILES, instance=pelicula)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Pelicula editada")
            return redirect("lista_peliculas")
    else:
        formulario = PeliculasForm(instance=pelicula)

    return render(request, "peliculas/nueva_pelicula.html", {"formulario": formulario})


def eliminar_pelicula(request, pk):
    pelicula = get_object_or_404(Peliculas, pk=pk)

    if request.method == "POST":
        pelicula.delete()
        messages.warning(request, "Pelicula eliminada")
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