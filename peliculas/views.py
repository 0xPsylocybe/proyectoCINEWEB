from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from usuarios.decorators import gestor_required
from . import tmdb
from .forms import PeliculasForm, GeneroForm,DirectorForm
from .models import Peliculas,Director,Genero


@gestor_required
def buscar_tmdb(request):
    """Devuelve en JSON la ficha de una película para rellenar el formulario.

    La usa el botón "Buscar en TMDB" del alta de película. No guarda la
    película: solo propone los datos para que el gestor los revise antes.
    """
    titulo = (request.GET.get("titulo") or "").strip()
    if not titulo:
        return JsonResponse({"error": "Escribe primero el título."}, status=400)

    try:
        ficha = tmdb.buscar(titulo, request.GET.get("anio") or None)
    except tmdb.ErrorTMDB as e:
        return JsonResponse({"error": str(e)}, status=502)

    if not ficha:
        return JsonResponse(
            {"error": 'TMDB no encuentra ninguna película llamada "%s".' % titulo},
            status=404)

    # El director y el género son claves ajenas: hay que tenerlos en la BBDD
    # para poder seleccionarlos en el desplegable.
    director = genero = None
    if ficha["director"]:
        director = (Director.objects.filter(nombre__iexact=ficha["director"]).first()
                    or Director.objects.create(nombre=ficha["director"]))
    if ficha["genero"]:
        genero = (Genero.objects.filter(nombre__iexact=ficha["genero"]).first()
                  or Genero.objects.create(nombre=ficha["genero"]))

    return JsonResponse({
        "titulo": ficha["titulo"],
        "sinopsis": tmdb.recortar_sinopsis(ficha["sinopsis"]),
        "duracion": ficha["duracion"],
        "anio": ficha["anio"],
        "puntuacion": ficha["puntuacion"],
        "director": {"id": director.id, "nombre": director.nombre} if director else None,
        "genero": {"id": genero.id, "nombre": genero.nombre} if genero else None,
        "poster": ficha["poster"],
        "poster_url": tmdb.IMG + ficha["poster"] if ficha["poster"] else None,
    })


@gestor_required
def crear_pelicula(request):
    if request.method == "POST":
        formulario = PeliculasForm(request.POST, request.FILES)

        if formulario.is_valid():
            pelicula = formulario.save(commit=False)

            # Si el gestor no subió cartel pero usó el buscador de TMDB,
            # se descarga el que propuso TMDB.
            poster = request.POST.get("poster_tmdb")
            if poster and not request.FILES.get("imagen"):
                try:
                    pelicula.imagen.save("%s.jpg" % tmdb.slug(pelicula.titulo),
                                         ContentFile(tmdb.descargar_cartel(poster)),
                                         save=False)
                except tmdb.ErrorTMDB:
                    messages.warning(request, "No se pudo descargar el cartel de TMDB.")

            puntuacion = request.POST.get("puntuacion_tmdb")
            if puntuacion:
                try:
                    pelicula.puntuacion = float(puntuacion)
                except ValueError:
                    pass

            pelicula.save()
            messages.success(request, "¡Película creada correctamente!")
            return redirect("lista_peliculas")
    else:
        formulario = PeliculasForm()

    return render(request, "peliculas/nueva_pelicula.html",
                  {"formulario": formulario, "hay_clave_tmdb": tmdb.hay_clave()})


@gestor_required
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


@gestor_required
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

    # Misma plantilla que el alta, así que el buscador de TMDB va también aquí
    return render(request, "peliculas/nueva_pelicula.html",
                  {"formulario": formulario, "hay_clave_tmdb": tmdb.hay_clave()})


@gestor_required
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