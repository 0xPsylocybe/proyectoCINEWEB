"""Sube a la base de datos los carteles que hasta ahora solo estaban en disco.

La carpeta `media/` está en .gitignore, así que los ficheros nunca llegaban al
equipo del compañero: la BBDD guardaba la ruta y allí no existía el fichero, y
las imágenes salían rotas. A partir de aquí el cartel viaja en la propia base
de datos, que sí es compartida.

Solo puede migrar lo que haya en el disco de quien la ejecute. Quien no tenga
los ficheros no perderá nada: los recupera con
`python manage.py importar_tmdb --conservar-titulos --solo-carteles`.
"""

import mimetypes
import os

from django.conf import settings
from django.db import migrations


def subir_carteles(apps, schema_editor):
    Peliculas = apps.get_model("peliculas", "Peliculas")
    CartelPelicula = apps.get_model("peliculas", "CartelPelicula")

    subidos, sin_fichero = 0, 0

    for pelicula in Peliculas.objects.exclude(imagen=""):
        ruta = os.path.join(settings.MEDIA_ROOT, pelicula.imagen.name)
        if not os.path.exists(ruta):
            sin_fichero += 1
            continue

        with open(ruta, "rb") as f:
            contenido = f.read()

        tipo = mimetypes.guess_type(ruta)[0] or "image/jpeg"
        CartelPelicula.objects.update_or_create(
            pelicula=pelicula, defaults={"datos": contenido, "tipo": tipo})
        subidos += 1

    if subidos or sin_fichero:
        print("\n   carteles subidos a la BBDD: %d" % subidos)
        if sin_fichero:
            print("   sin fichero en este equipo: %d "
                  "(recuperables con importar_tmdb --solo-carteles)" % sin_fichero)


def borrar_carteles(apps, schema_editor):
    apps.get_model("peliculas", "CartelPelicula").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("peliculas", "0005_cartelpelicula"),
    ]

    operations = [
        migrations.RunPython(subir_carteles, borrar_carteles),
    ]
