"""Lectura del fichero .env.

Sin dependencias externas: `settings.py` lo llama antes de nada para que las
credenciales estén en `os.environ` y no escritas en el código.

El `.env` está en .gitignore. Cada equipo necesita el suyo; en `.env.example`
está la plantilla con las claves que hacen falta.
"""

import os


def cargar_env(ruta):
    """Vuelca el .env en os.environ. Lo que ya esté definido en el entorno
    manda sobre el fichero."""
    if not os.path.exists(ruta):
        return

    with open(ruta, encoding="utf-8") as fichero:
        for linea in fichero:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            clave = clave.strip()
            valor = valor.strip().strip('"').strip("'")
            os.environ.setdefault(clave, valor)


def obligatoria(clave, por_defecto=None):
    """Devuelve una variable de entorno; si falta y no hay valor por defecto,
    avisa de qué hay que configurar en vez de fallar con un error críptico."""
    valor = os.environ.get(clave, por_defecto)
    if valor is None:
        raise RuntimeError(
            "Falta la variable %s.\n"
            "Copia .env.example a .env y rellena sus valores.\n"
            "El fichero .env no se sube al repositorio: pídeselos a tu compañero."
            % clave
        )
    return valor


def booleana(clave, por_defecto=False):
    valor = os.environ.get(clave)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes", "on")
