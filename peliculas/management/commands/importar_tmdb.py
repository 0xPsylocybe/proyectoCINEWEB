"""Completa las películas con datos reales de TMDB: cartel, sinopsis,
duración, año, género y director.

Uso:
    python manage.py importar_tmdb --dry-run   # enseña qué haría, sin tocar nada
    python manage.py importar_tmdb             # aplica los cambios
    python manage.py importar_tmdb --solo-carteles

La clave de TMDB se lee de la variable de entorno TMDB_API_KEY o del
fichero .env del proyecto (TMDB_API_KEY=...). El .env está en .gitignore.
"""

import time
import urllib.error
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from peliculas import tmdb
from peliculas.models import DetallePelicula, Director, Genero, Peliculas

# Títulos inventados por la carga inicial -> película real equivalente.
# La clave es el título tal cual está en la BBDD.
SUSTITUCIONES = {
    "Oppenheimer 2": ("Oppenheimer", 2023),
    "Avatar 4": ("Avatar: Fire and Ash", 2025),
    "Dune: Profecia": ("Dune: Part Two", 2024),
    "Crepusculo Eterno": ("Little Women", 2019),
    "Fantasia Invisible": ("Eddington", 2025),
    "Risa en la Noche": ("Jojo Rabbit", 2019),
    "The Thousand Autumns": ("In the Mood for Love", 2000),
    "Capitan America: Sentinela del Atlantico": ("Captain America: Brave New World", 2025),
    "Neon Genesis Evangelion": ("Evangelion: 3.0+1.0 Thrice Upon a Time", 2021),
    "El Conde": ("El Conde", 2023),
    "Gladiador II": ("Gladiator II", 2024),
    "Mufasa: El Rey Leon": ("Mufasa: The Lion King", 2024),
    "Sonic 3": ("Sonic the Hedgehog 3", 2024),
}


class Command(BaseCommand):
    help = "Rellena carteles y fichas de las películas desde TMDB"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Muestra los cambios sin guardarlos")
        parser.add_argument("--solo-carteles", action="store_true",
                            help="Descarga solo el cartel, sin tocar los demás campos")
        parser.add_argument("--conservar-titulos", action="store_true",
                            help="Mantiene título, género y director de la BBDD, y toma de "
                                 "TMDB solo cartel, sinopsis, duración y año. TMDB añade "
                                 "coletillas como 'Del revés 2 (Inside Out 2)'")
        parser.add_argument("--api-key", help="Clave de TMDB (si no, se lee de .env)")

    def handle(self, *args, **opciones):
        clave = opciones.get("api_key") or tmdb.leer_api_key()
        if not clave:
            raise CommandError(
                "Falta la clave de TMDB.\n"
                "Crea un fichero .env en la raíz del proyecto con:\n"
                "    TMDB_API_KEY=tu_clave\n"
                "La sacas gratis en https://www.themoviedb.org/settings/api"
            )

        ensayo = opciones["dry_run"]
        solo_carteles = opciones["solo_carteles"]

        if ensayo:
            self.stdout.write(self.style.WARNING("ENSAYO: no se guarda nada\n"))

        aciertos, fallos = 0, []

        for pelicula in Peliculas.objects.select_related("director", "genero").order_by("titulo"):
            titulo_busqueda, anio_busqueda = SUSTITUCIONES.get(
                pelicula.titulo, (pelicula.titulo, pelicula.anio)
            )

            try:
                ficha = self.buscar(clave, titulo_busqueda, anio_busqueda)
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    raise CommandError("TMDB rechaza la clave (401). Revisa TMDB_API_KEY.")
                fallos.append((pelicula.titulo, "HTTP %s" % e.code))
                continue
            except Exception as e:
                fallos.append((pelicula.titulo, type(e).__name__))
                continue

            if not ficha:
                fallos.append((pelicula.titulo, "sin resultados en TMDB"))
                continue

            cambio = "=" if ficha["titulo"] == pelicula.titulo else "->"
            self.stdout.write("%-42s %s %s" % (
                pelicula.titulo[:42], cambio,
                ficha["titulo"] if cambio == "->" else ""))

            if not ensayo:
                self.aplicar(pelicula, ficha, solo_carteles, opciones["conservar_titulos"])

            self.stdout.write("    %s · %s · %s min · %s · nota %s" % (
                ficha["anio"], ficha["director"] or "?", ficha["duracion"] or "?",
                ficha["genero"] or "?", ficha["puntuacion"] or "?"))
            self.stdout.write("    cartel: %s" % (ficha["poster"] or "NO HAY"))

            aciertos += 1
            time.sleep(0.25)   # cortesía con la API

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Resueltas: %d" % aciertos))
        if fallos:
            self.stdout.write(self.style.ERROR("Sin resolver: %d" % len(fallos)))
            for titulo, motivo in fallos:
                self.stdout.write("   - %s (%s)" % (titulo, motivo))

    def buscar(self, clave, titulo, anio):
        """Busca la película y devuelve su ficha ya normalizada."""
        return tmdb.buscar(titulo, anio, clave=clave)

    def aplicar(self, pelicula, ficha, solo_carteles, conservar_titulos=False):
        if not solo_carteles:
            # La puntuación se actualiza siempre: no es un dato que corrijamos a mano
            if ficha["puntuacion"]:
                pelicula.puntuacion = ficha["puntuacion"]
            if not conservar_titulos:
                pelicula.titulo = ficha["titulo"]
            if ficha["sinopsis"]:
                pelicula.sinopsis = tmdb.recortar_sinopsis(ficha["sinopsis"])
            if ficha["duracion"]:
                pelicula.duracion = timedelta(minutes=ficha["duracion"])
            if ficha["anio"]:
                pelicula.anio = ficha["anio"]
            if ficha["director"] and not conservar_titulos:
                pelicula.director = Director.objects.filter(
                    nombre__iexact=ficha["director"]).first() or Director.objects.create(
                    nombre=ficha["director"])
            if ficha["genero"] and not conservar_titulos:
                pelicula.genero = Genero.objects.filter(
                    nombre__iexact=ficha["genero"]).first() or Genero.objects.create(
                    nombre=ficha["genero"])

            if ficha["estreno"]:
                detalle = DetallePelicula.objects.filter(pelicula=pelicula).first()
                if detalle:
                    detalle.fecha_estreno = ficha["estreno"]
                    detalle.save(update_fields=["fecha_estreno"])

        if ficha["poster"]:
            self.descargar_cartel(pelicula, ficha["poster"])

        pelicula.save()

    def descargar_cartel(self, pelicula, poster_path):
        contenido = tmdb.descargar_cartel(poster_path)
        pelicula.imagen.save("%s.jpg" % tmdb.slug(pelicula.titulo),
                             ContentFile(contenido), save=False)
