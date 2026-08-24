"""Completa las películas con datos reales de TMDB: cartel, sinopsis,
duración, año, género y director.

Uso:
    python manage.py importar_tmdb --dry-run   # enseña qué haría, sin tocar nada
    python manage.py importar_tmdb             # aplica los cambios
    python manage.py importar_tmdb --solo-carteles

La clave de TMDB se lee de la variable de entorno TMDB_API_KEY o del
fichero .env del proyecto (TMDB_API_KEY=...). El .env está en .gitignore.
"""

import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from peliculas.models import DetallePelicula, Director, Genero, Peliculas

API = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"

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


def leer_api_key():
    clave = os.environ.get("TMDB_API_KEY")
    if clave:
        return clave.strip()

    env = os.path.join(settings.BASE_DIR, ".env")
    if os.path.exists(env):
        with open(env, encoding="utf-8") as f:
            for linea in f:
                if linea.strip().startswith("TMDB_API_KEY"):
                    return linea.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def pedir(url):
    peticion = urllib.request.Request(url, headers={"User-Agent": "CINEWEB/1.0"})
    with urllib.request.urlopen(peticion, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def slug(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


class Command(BaseCommand):
    help = "Rellena carteles y fichas de las películas desde TMDB"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Muestra los cambios sin guardarlos")
        parser.add_argument("--solo-carteles", action="store_true",
                            help="Descarga solo el cartel, sin tocar los demás campos")
        parser.add_argument("--api-key", help="Clave de TMDB (si no, se lee de .env)")

    def handle(self, *args, **opciones):
        clave = opciones.get("api_key") or leer_api_key()
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
                self.aplicar(pelicula, ficha, solo_carteles)

            self.stdout.write("    %s · %s · %s min · %s" % (
                ficha["anio"], ficha["director"] or "?", ficha["duracion"] or "?",
                ficha["genero"] or "?"))
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
        params = {"api_key": clave, "query": titulo, "language": "es-ES"}
        if anio:
            params["year"] = anio
        datos = pedir("%s/search/movie?%s" % (API, urllib.parse.urlencode(params)))

        resultados = datos.get("results") or []
        if not resultados and anio:
            # Reintenta sin año: a veces el año de la BBDD no es el de estreno
            params.pop("year")
            resultados = (pedir("%s/search/movie?%s" % (API, urllib.parse.urlencode(params)))
                          .get("results") or [])
        if not resultados:
            return None

        detalle = pedir("%s/movie/%s?%s" % (
            API, resultados[0]["id"],
            urllib.parse.urlencode({"api_key": clave, "language": "es-ES",
                                    "append_to_response": "credits"})))

        director = next((p["name"] for p in detalle.get("credits", {}).get("crew", [])
                         if p.get("job") == "Director"), None)
        generos = detalle.get("genres") or []
        estreno = detalle.get("release_date") or ""

        return {
            "titulo": detalle.get("title") or titulo,
            "sinopsis": (detalle.get("overview") or "").strip(),
            "duracion": detalle.get("runtime") or 0,
            "anio": int(estreno[:4]) if estreno[:4].isdigit() else anio,
            "estreno": estreno,
            "director": director,
            "genero": generos[0]["name"] if generos else None,
            "poster": detalle.get("poster_path"),
        }

    def aplicar(self, pelicula, ficha, solo_carteles):
        if not solo_carteles:
            pelicula.titulo = ficha["titulo"]
            if ficha["sinopsis"]:
                # sinopsis es CharField(300): cortamos por palabra
                texto = ficha["sinopsis"]
                if len(texto) > 300:
                    texto = texto[:297].rsplit(" ", 1)[0] + "..."
                pelicula.sinopsis = texto
            if ficha["duracion"]:
                pelicula.duracion = timedelta(minutes=ficha["duracion"])
            if ficha["anio"]:
                pelicula.anio = ficha["anio"]
            if ficha["director"]:
                pelicula.director = Director.objects.get_or_create(
                    nombre=ficha["director"])[0]
            if ficha["genero"]:
                pelicula.genero = Genero.objects.get_or_create(
                    nombre=ficha["genero"])[0]

            if ficha["estreno"]:
                detalle = DetallePelicula.objects.filter(pelicula=pelicula).first()
                if detalle:
                    detalle.fecha_estreno = ficha["estreno"]
                    detalle.save(update_fields=["fecha_estreno"])

        if ficha["poster"]:
            self.descargar_cartel(pelicula, ficha["poster"])

        pelicula.save()

    def descargar_cartel(self, pelicula, poster_path):
        peticion = urllib.request.Request(IMG + poster_path,
                                          headers={"User-Agent": "CINEWEB/1.0"})
        with urllib.request.urlopen(peticion, timeout=30) as r:
            contenido = r.read()

        pelicula.imagen.save("%s.jpg" % slug(pelicula.titulo),
                             ContentFile(contenido), save=False)
