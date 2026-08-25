"""Acceso a la API de TMDB.

Lo usan el comando `importar_tmdb` (en lote) y el botón "Buscar en TMDB" del
formulario de alta de película (una a una).

La clave se lee de la variable de entorno TMDB_API_KEY o del fichero .env del
proyecto. El .env está en .gitignore, así que **cada equipo necesita el suyo**:
si no hay clave, `hay_clave()` devuelve False y quien llame debe apañárselas
sin TMDB en vez de reventar.
"""

import json
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

API = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"


class ErrorTMDB(Exception):
    """Algo fue mal hablando con TMDB (sin clave, clave inválida, red...)."""


def leer_api_key():
    """Obtiene la clave de API de TMDB desde las variables de entorno o el archivo .env."""
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


def hay_clave():
    """Para poder ocultar el botón en los equipos que no tengan .env."""
    return bool(leer_api_key())


def es_token_v4(clave):
    """El token v4 de TMDB es un JWT; la API key v3 es una cadena hexadecimal."""
    return clave.count(".") == 2 and clave.startswith("ey")


def pedir(url, clave):
    """Realiza una petición HTTP a la API de TMDB y devuelve la respuesta en formato JSON."""
    cabeceras = {"User-Agent": "CINEWEB/1.0"}
    if es_token_v4(clave):
        cabeceras["Authorization"] = "Bearer %s" % clave
    peticion = urllib.request.Request(url, headers=cabeceras)
    with urllib.request.urlopen(peticion, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def con_clave(params, clave):
    """La v3 viaja en la URL; la v4 va en la cabecera y no debe ir aquí."""
    if not es_token_v4(clave):
        params["api_key"] = clave
    return params


def slug(texto):
    """Genera un slug limpio y sin caracteres especiales a partir de un texto."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def buscar(titulo, anio=None, clave=None):
    """Busca una película por título y devuelve su ficha normalizada.

    Devuelve None si TMDB no encuentra nada. Lanza ErrorTMDB si no hay clave
    o si la API responde mal.
    """
    clave = clave or leer_api_key()
    if not clave:
        raise ErrorTMDB(
            "No hay clave de TMDB. Crea un fichero .env en la raíz del proyecto "
            "con TMDB_API_KEY=tu_clave (se saca gratis en themoviedb.org)."
        )

    params = con_clave({"query": titulo, "language": "es-ES"}, clave)
    if anio:
        params["year"] = anio

    try:
        datos = pedir("%s/search/movie?%s" % (API, urllib.parse.urlencode(params)), clave)
        resultados = datos.get("results") or []

        if not resultados and anio:
            # Reintenta sin año: a veces el año que consta no es el de estreno
            params.pop("year")
            resultados = (pedir("%s/search/movie?%s" % (API, urllib.parse.urlencode(params)),
                                clave).get("results") or [])
        if not resultados:
            return None

        detalle = pedir("%s/movie/%s?%s" % (
            API, resultados[0]["id"],
            urllib.parse.urlencode(con_clave({"language": "es-ES",
                                              "append_to_response": "credits"}, clave))),
            clave)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise ErrorTMDB("TMDB rechaza la clave. Revisa TMDB_API_KEY en el .env.")
        raise ErrorTMDB("TMDB respondió con un error %s." % e.code)
    except urllib.error.URLError:
        raise ErrorTMDB("No se ha podido conectar con TMDB. ¿Hay conexión?")

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
        # Nota media de TMDB sobre 10 (no es la de IMDb, que TMDB no expone)
        "puntuacion": round(detalle.get("vote_average") or 0, 1),
    }


def descargar_cartel(poster_path):
    """Baja el cartel y devuelve los bytes. `poster_path` viene de buscar()."""
    peticion = urllib.request.Request(IMG + poster_path,
                                      headers={"User-Agent": "CINEWEB/1.0"})
    try:
        with urllib.request.urlopen(peticion, timeout=30) as r:
            return r.read()
    except (urllib.error.HTTPError, urllib.error.URLError):
        raise ErrorTMDB("No se ha podido descargar el cartel.")


def recortar_sinopsis(texto, limite=300):
    """La sinopsis es un CharField(300): se corta por palabra."""
    if len(texto) <= limite:
        return texto
    return texto[:limite - 3].rsplit(" ", 1)[0] + "..."
