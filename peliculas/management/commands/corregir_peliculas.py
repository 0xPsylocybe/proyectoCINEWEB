"""Corrige los datos que la carga inicial dejó mal: títulos inventados,
directores equivocados, años, duraciones, géneros y sinopsis.

Los datos se han escrito a mano. Cuando haya clave de TMDB, `importar_tmdb`
los refina y añade los carteles.

Uso:
    python manage.py corregir_peliculas --dry-run
    python manage.py corregir_peliculas
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from peliculas.models import Director, Genero, Peliculas

# titulo_en_bbdd: (titulo, director, anio, minutos, genero, sinopsis)
CORRECCIONES = {
    # --- Películas reales: se corrige lo que estaba mal ---
    "Pulp Fiction": (
        "Pulp Fiction", "Quentin Tarantino", 1994, 154, "Crimen",
        "Las historias de dos sicarios, un boxeador y la mujer de un mafioso se "
        "entrecruzan en Los Ángeles en un relato contado fuera de orden."),
    "The Shawshank Redemption": (
        "Cadena perpetua", "Frank Darabont", 1994, 142, "Drama",
        "Un banquero condenado por un crimen que no cometió se gana el respeto de "
        "sus compañeros de presidio mientras urde su plan durante dos décadas."),
    "La Haine": (
        "El odio", "Mathieu Kassovitz", 1995, 98, "Drama",
        "Veinticuatro horas en la vida de tres jóvenes de los suburbios de París "
        "tras una noche de disturbios contra la policía."),
    "Mulholland Drive": (
        "Mulholland Drive", "David Lynch", 2001, 147, "Misterio",
        "Una aspirante a actriz recién llegada a Los Ángeles ayuda a una mujer "
        "amnésica a reconstruir su identidad, y la realidad empieza a resquebrajarse."),
    "The Dark Knight": (
        "El caballero oscuro", "Christopher Nolan", 2008, 152, "Acción",
        "Batman se enfrenta al Joker, un criminal que no busca dinero ni poder, "
        "sino demostrar que cualquiera puede caer en el caos."),
    "Inception": (
        "Origen", "Christopher Nolan", 2010, 148, "Ciencia ficción",
        "Un ladrón capaz de entrar en los sueños ajenos acepta el encargo imposible "
        "de implantar una idea en la mente de un empresario."),
    "Interstellar": (
        "Interstellar", "Christopher Nolan", 2014, 169, "Ciencia ficción",
        "Con la Tierra agonizando, un piloto deja a su familia para cruzar un agujero "
        "de gusano en busca de un planeta habitable."),
    "Parasite": (
        "Parásitos", "Bong Joon-ho", 2019, 132, "Thriller",
        "Una familia sin recursos se infiltra uno a uno en el servicio de una casa "
        "adinerada, hasta que un descubrimiento lo desborda todo."),
    "Dune": (
        "Dune", "Denis Villeneuve", 2021, 155, "Ciencia ficción",
        "El heredero de la casa Atreides viaja al planeta desértico Arrakis, única "
        "fuente de la especia más valiosa del universo."),
    "American Fiction": (   # el director estaba mal
        "American Fiction", "Cord Jefferson", 2023, 117, "Comedia",
        "Un novelista harto de los tópicos sobre la vida afroamericana escribe una "
        "parodia con seudónimo, y el libro se convierte en un éxito enorme."),
    "Barbie": (
        "Barbie", "Greta Gerwig", 2023, 114, "Comedia",
        "Barbie abandona Barbieland rumbo al mundo real para descubrir por qué su "
        "vida perfecta ha empezado a fallar."),
    "Godzilla Minus One": (
        "Godzilla Minus One", "Takashi Yamazaki", 2023, 125, "Acción",
        "En un Japón devastado por la posguerra, un piloto marcado por la culpa se "
        "enfrenta a la aparición de una criatura colosal."),
    "Killers of the Flower Moon": (
        "Los asesinos de la luna", "Martin Scorsese", 2023, 206, "Crimen",
        "En los años veinte, los miembros de la nación Osage empiezan a ser "
        "asesinados uno tras otro después de hallarse petróleo en sus tierras."),
    "Past Lives": (   # el director estaba mal
        "Vidas pasadas", "Celine Song", 2023, 105, "Romance",
        "Dos amigos de la infancia separados por la emigración se reencuentran en "
        "Nueva York veinte años después, con la vida ya encaminada."),
    "Saltburn": (
        "Saltburn", "Emerald Fennell", 2023, 131, "Thriller",
        "Un estudiante becado en Oxford es invitado a pasar el verano en la finca "
        "familiar de su carismático compañero de clase."),
    "The Brutalist": (
        "The Brutalist", "Brady Corbet", 2024, 215, "Drama",
        "Un arquitecto húngaro superviviente del Holocausto emigra a Estados Unidos, "
        "donde un encargo monumental le da fama y lo consume."),
    "The Iron Claw": (
        "The Iron Claw", "Sean Durkin", 2023, 132, "Drama",
        "La historia real de los hermanos Von Erich, una dinastía de luchadores "
        "perseguida por la ambición de su padre y por la tragedia."),
    "The Zone of Interest": (   # el director estaba mal
        "La zona de interés", "Jonathan Glazer", 2023, 105, "Drama",
        "El comandante de Auschwitz y su mujer construyen una vida familiar apacible "
        "en una casa pegada al muro del campo."),
    "Gladiador II": (
        "Gladiador II", "Ridley Scott", 2024, 148, "Acción",
        "Años después de la muerte de Máximo, un joven llega a la arena del Coliseo "
        "decidido a vengarse del imperio que le arrebató su hogar."),
    "Inside Out 2": (
        "Del revés 2", "Kelsey Mann", 2024, 96, "Animación",
        "Riley llega a la adolescencia y en su cabeza aparecen emociones nuevas, "
        "con Ansiedad dispuesta a tomar el mando."),
    "Moana 2": (
        "Vaiana 2", "David Derrick Jr.", 2024, 100, "Animación",
        "Vaiana vuelve a hacerse a la mar, esta vez con tripulación, siguiendo la "
        "llamada de sus antepasados hacia aguas desconocidas."),
    "Mufasa: El Rey Leon": (
        "Mufasa: El Rey León", "Barry Jenkins", 2024, 118, "Animación",
        "La historia de cómo un cachorro huérfano y perdido llegó a convertirse en "
        "el rey de la sabana."),
    "Sonic 3": (
        "Sonic 3: La película", "Jeff Fowler", 2024, 110, "Aventura",
        "Sonic y sus amigos se ven obligados a aliarse con su peor enemigo para "
        "frenar a un adversario surgido del pasado."),
    "Wicked": (
        "Wicked", "Jon M. Chu", 2024, 160, "Musical",
        "La amistad entre dos estudiantes de magia muy distintas explica cómo una "
        "acabó siendo la Bruja Mala del Oeste y la otra, la Bruja Buena."),
    "Nosferatu": (
        "Nosferatu", "Robert Eggers", 2024, 132, "Terror",
        "Una joven recién casada se convierte en la obsesión de un antiguo conde "
        "que arrastra la peste allá por donde pasa."),
    "El Conde": (   # el director estaba mal
        "El Conde", "Pablo Larraín", 2023, 110, "Comedia",
        "Sátira en la que Pinochet no murió, sino que lleva siglos siendo un vampiro "
        "y ahora, cansado, quiere dejar de vivir."),
    "Capitan America: Sentinela del Atlantico": (
        "Capitán América: Brave New World", "Julius Onah", 2025, 118, "Acción",
        "Sam Wilson estrena el escudo del Capitán América en plena crisis "
        "internacional y descubre una conspiración en marcha."),

    # --- Títulos inventados: se sustituyen por películas reales ---
    "Neon Genesis Evangelion": (
        "Evangelion: 3.0+1.0 Thrice Upon a Time", "Hideaki Anno", 2021, 155, "Animación",
        "Cierre de la saga: con la humanidad al borde del final, Shinji debe decidir "
        "qué mundo merece quedar en pie."),
    "The Thousand Autumns": (
        "Deseando amar", "Wong Kar-wai", 2000, 98, "Romance",
        "Dos vecinos descubren que sus cónyuges les son infieles entre sí y se "
        "acompañan en un afecto que nunca llegan a nombrar."),
    "Crepusculo Eterno": (
        "Mujercitas", "Greta Gerwig", 2019, 135, "Drama",
        "Las cuatro hermanas March crecen en la Nueva Inglaterra de la guerra civil "
        "mientras Jo pelea por vivir de la escritura."),
    "Fantasia Invisible": (
        "Beau tiene miedo", "Ari Aster", 2023, 179, "Terror",
        "Un hombre atenazado por la ansiedad emprende el viaje de vuelta a casa de "
        "su madre, y el trayecto se vuelve una pesadilla sin fondo."),
    "Risa en la Noche": (
        "Jojo Rabbit", "Taika Waititi", 2019, 108, "Comedia",
        "Un niño de las juventudes hitlerianas, cuyo amigo imaginario es Hitler, "
        "descubre que su madre esconde a una chica judía en casa."),
    "Avatar 4": (
        "Avatar: El sentido del agua", "James Cameron", 2022, 192, "Ciencia ficción",
        "Jake Sully y Neytiri huyen con sus hijos hacia los arrecifes de Pandora "
        "buscando refugio entre los clanes del agua."),
    "Dune: Profecia": (
        "Dune: Parte Dos", "Denis Villeneuve", 2024, 166, "Ciencia ficción",
        "Paul Atreides se une a los fremen para vengar a su familia, mientras teme "
        "convertirse en la figura mesiánica que anuncian las profecías."),
    "Oppenheimer 2": (
        "Oppenheimer", "Christopher Nolan", 2023, 180, "Drama",
        "El físico que dirigió el Proyecto Manhattan carga después con las "
        "consecuencias de haber puesto la bomba atómica en el mundo."),
}


def buscar_o_crear(modelo, nombre):
    """Reutiliza el registro que ya exista aunque difiera en mayúsculas o
    acentos, para no acabar con 'Ciencia Ficción' y 'Ciencia ficción'."""
    existente = modelo.objects.filter(nombre__iexact=nombre).first()
    return existente or modelo.objects.create(nombre=nombre)


class Command(BaseCommand):
    help = "Corrige títulos, directores, años, duraciones, géneros y sinopsis"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Muestra los cambios sin guardarlos")

    def handle(self, *args, **opciones):
        ensayo = opciones["dry_run"]
        if ensayo:
            self.stdout.write(self.style.WARNING("ENSAYO: no se guarda nada\n"))

        tocadas, intactas, ausentes = 0, 0, []

        with transaction.atomic():
            for clave, datos in CORRECCIONES.items():
                titulo, director, anio, minutos, genero, sinopsis = datos

                pelicula = Peliculas.objects.filter(titulo=clave).first()
                if not pelicula:
                    ausentes.append(clave)
                    continue

                cambios = []
                if pelicula.titulo != titulo:
                    cambios.append('título: "%s" -> "%s"' % (pelicula.titulo, titulo))
                if not pelicula.director or pelicula.director.nombre.lower() != director.lower():
                    actual = pelicula.director.nombre if pelicula.director else "?"
                    cambios.append("director: %s -> %s" % (actual, director))
                if pelicula.anio != anio:
                    cambios.append("año: %s -> %s" % (pelicula.anio, anio))
                nueva_duracion = timedelta(minutes=minutos)
                if pelicula.duracion != nueva_duracion:
                    cambios.append("duración: %s -> %s min" % (pelicula.duracion, minutos))
                if not pelicula.genero or pelicula.genero.nombre.lower() != genero.lower():
                    actual = pelicula.genero.nombre if pelicula.genero else "?"
                    cambios.append("género: %s -> %s" % (actual, genero))
                if pelicula.sinopsis != sinopsis:
                    cambios.append("sinopsis reescrita")

                if not cambios:
                    intactas += 1
                    continue

                self.stdout.write(self.style.HTTP_INFO(clave))
                for c in cambios:
                    self.stdout.write("    %s" % c)

                if not ensayo:
                    pelicula.titulo = titulo
                    pelicula.director = buscar_o_crear(Director, director)
                    pelicula.genero = buscar_o_crear(Genero, genero)
                    pelicula.anio = anio
                    pelicula.duracion = nueva_duracion
                    pelicula.sinopsis = sinopsis
                    pelicula.save()

                tocadas += 1

            if ensayo:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Corregidas: %d" % tocadas))
        if intactas:
            self.stdout.write("Ya estaban bien: %d" % intactas)
        if ausentes:
            self.stdout.write(self.style.ERROR("No encontradas en la BBDD: %d" % len(ausentes)))
            for t in ausentes:
                self.stdout.write("   - %s" % t)

        # Directores y géneros que se quedan sin ninguna película
        huerfanos = Director.objects.filter(peliculas__isnull=True)
        if huerfanos.exists():
            nombres = ", ".join(d.nombre for d in huerfanos)
            self.stdout.write(self.style.WARNING(
                "\nDirectores ya sin películas: %s" % nombres))
