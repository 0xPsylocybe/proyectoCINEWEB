import os

from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from usuarios.decorators import gestor_required
from . import tmdb
from .forms import PeliculasForm, GeneroForm,DirectorForm
from .models import CartelPelicula, Peliculas,Director,Genero


def cartel_pelicula(request, pk):
    """Sirve el cartel guardado en la base de datos.

    Si esa película todavía no lo tiene en la BBDD, cae al fichero de `media/`
    (equipos que aún no hayan migrado). Es público: los carteles se ven en la
    cartelera sin necesidad de iniciar sesión.
    """
    pelicula = get_object_or_404(Peliculas, pk=pk)

    cartel = CartelPelicula.objects.filter(pelicula=pelicula).first()
    if cartel:
        respuesta = HttpResponse(bytes(cartel.datos), content_type=cartel.tipo)
        # El cartel de una película no cambia casi nunca
        respuesta["Cache-Control"] = "public, max-age=86400"
        return respuesta

    if pelicula.imagen and os.path.exists(pelicula.imagen.path):
        return FileResponse(pelicula.imagen.open("rb"))

    raise Http404("Esta película no tiene cartel.")


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


def _guardar_cartel(request, pelicula, formulario):
    """Lleva el cartel a la BBDD, venga del fichero subido o de TMDB.

    Se llama con la película ya guardada, porque el cartel cuelga de ella.
    """
    subida = request.FILES.get("imagen")
    poster = request.POST.get("poster_tmdb")

    if subida:
        # El formulario ya dejó el fichero en `imagen`; falta la copia en BBDD,
        # que es lo único que se comparte entre equipos.
        subida.seek(0)
        pelicula.guardar_cartel(subida.read(),
                                tipo=getattr(subida, "content_type", None) or "image/jpeg")
    elif poster:
        try:
            pelicula.guardar_cartel(tmdb.descargar_cartel(poster),
                                    "%s.jpg" % tmdb.slug(pelicula.titulo))
            pelicula.save(update_fields=["imagen"])
        except tmdb.ErrorTMDB:
            messages.warning(request, "No se pudo descargar el cartel de TMDB.")


@gestor_required
def crear_pelicula(request):
    if request.method == "POST":
        formulario = PeliculasForm(request.POST, request.FILES)

        if formulario.is_valid():
            pelicula = formulario.save(commit=False)

            puntuacion = request.POST.get("puntuacion_tmdb")
            if puntuacion:
                try:
                    pelicula.puntuacion = float(puntuacion)
                except ValueError:
                    pass

            # Hay que guardarla antes: el cartel cuelga de ella y necesita su id
            pelicula.save()
            _guardar_cartel(request, pelicula, formulario)

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
            pelicula = formulario.save()
            _guardar_cartel(request, pelicula, formulario)
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