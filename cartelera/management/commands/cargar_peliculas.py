from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from peliculas.models import Peliculas, Director, Genero, DetallePelicula
from cartelera.models import Sala, Sesion
import random


class Command(BaseCommand):
    help = 'Carga pelculas, directores, gneros y sesiones de prueba'

    def handle(self, *args, **options):
        # Crear gneros
        print("Creando generos...")
        generos_data = [
            'Accin', 'Comedia', 'Drama', 'Ciencia Ficcin',
            'Thriller', 'Aventura', 'Animacin', 'Romance',
            'Terror', 'Fantasa'
        ]
        generos = {}
        for genero_nombre in generos_data:
            genero, created = Genero.objects.get_or_create(nombre=genero_nombre)
            generos[genero_nombre] = genero
            if created:
                self.stdout.write(self.style.SUCCESS(f' Gnero: {genero_nombre}'))

        # Crear directores
        print("\nCreando directores...")
        directores_data = [
            'Christopher Nolan', 'Denis Villeneuve', 'Damien Chazelle',
            'Ari Aster', 'Greta Gerwig', 'Taika Waititi', 'James Gunn',
            'Wong Kar-wai', 'Yorgos Lanthimos', 'Paul Thomas Anderson',
            'Bong Joon-ho', 'Pedro Almodvar', 'Wes Anderson', 'David Fincher'
        ]
        directores = {}
        for director_nombre in directores_data:
            director, created = Director.objects.get_or_create(nombre=director_nombre)
            directores[director_nombre] = director
            if created:
                self.stdout.write(self.style.SUCCESS(f' Director: {director_nombre}'))

        # Datos de pelculas reales (2025-2026)
        print("\n Creando pelculas...")
        peliculas_data = [
            # Pelculas en cartelera (10-15)
            {
                'titulo': 'Dune: Profeca',
                'duracion': timedelta(minutes=166),
                'director': 'Denis Villeneuve',
                'genero': 'Ciencia Ficcin',
                'sinopsis': 'La historia del ascenso de los Bene Gesserit y su cofrada secreta.',
                'anio': 2026,
                'en_cartelera': True,
                'destacada': True
            },
            {
                'titulo': 'Oppenheimer 2',
                'duracion': timedelta(minutes=180),
                'director': 'Christopher Nolan',
                'genero': 'Drama',
                'sinopsis': 'Contina la historia del padre de la bomba atmica.',
                'anio': 2026,
                'en_cartelera': True,
                'destacada': True
            },
            {
                'titulo': 'Avatar 4',
                'duracion': timedelta(minutes=200),
                'director': 'James Cameron',
                'genero': 'Ciencia Ficcin',
                'sinopsis': 'La saga contina en Pandora con nuevos mundos y aventuras.',
                'anio': 2026,
                'en_cartelera': True,
                'destacada': True
            },
            {
                'titulo': 'Nosferatu',
                'duracion': timedelta(minutes=132),
                'director': 'Robert Eggers',
                'genero': 'Terror',
                'sinopsis': 'Remake del clsico del cine gtico alemn.',
                'anio': 2025,
                'en_cartelera': True,
                'destacada': False
            },
            {
                'titulo': 'Wicked',
                'duracion': timedelta(minutes=161),
                'director': 'Jon M. Chu',
                'genero': 'Fantasa',
                'sinopsis': 'La historia de la Bruja Malvada del Oeste antes de conocer a Dorothy.',
                'anio': 2024,
                'en_cartelera': True,
                'destacada': True
            },
            {
                'titulo': 'Gladiador II',
                'duracion': timedelta(minutes=148),
                'director': 'Ridley Scott',
                'genero': 'Accin',
                'sinopsis': 'La venganza en la arena romana contina.',
                'anio': 2024,
                'en_cartelera': True,
                'destacada': True
            },
            {
                'titulo': 'Mufasa: El Rey Len',
                'duracion': timedelta(minutes=145),
                'director': 'Barry Jenkins',
                'genero': 'Animacin',
                'sinopsis': 'La historia de origen del Rey Len.',
                'anio': 2024,
                'en_cartelera': True,
                'destacada': False
            },
            {
                'titulo': 'Sonic 3',
                'duracion': timedelta(minutes=104),
                'director': 'Jeff Fowler',
                'genero': 'Accin',
                'sinopsis': 'Sonic enfrenta su mayor desafo junto a sus amigos.',
                'anio': 2024,
                'en_cartelera': True,
                'destacada': False
            },
            {
                'titulo': 'Moana 2',
                'duracion': timedelta(minutes=100),
                'director': 'David Derrick Jr.',
                'genero': 'Animacin',
                'sinopsis': 'Moana regresa para una nueva aventura en el ocano.',
                'anio': 2024,
                'en_cartelera': True,
                'destacada': False
            },
            {
                'titulo': 'Capitn Amrica: Sentinela del Atlntico',
                'duracion': timedelta(minutes=151),
                'director': 'Julius Onah',
                'genero': 'Accin',
                'sinopsis': 'El nuevo Capitn Amrica en su primera misin en solitario.',
                'anio': 2025,
                'en_cartelera': True,
                'destacada': True
            },
            {
                'titulo': 'El Conde',
                'duracion': timedelta(minutes=112),
                'director': 'Jernimo Rodrguez',
                'genero': 'Drama',
                'sinopsis': 'Drama histrico sobre la vida de un conde europeo.',
                'anio': 2025,
                'en_cartelera': True,
                'destacada': False
            },
            {
                'titulo': 'Fantasa Invisible',
                'duracion': timedelta(minutes=118),
                'director': 'Ari Aster',
                'genero': 'Thriller',
                'sinopsis': 'Un thriller psicolgico que desafa la realidad.',
                'anio': 2025,
                'en_cartelera': True,
                'destacada': False
            },
            {
                'titulo': 'Crepsculo Eterno',
                'duracion': timedelta(minutes=125),
                'director': 'Greta Gerwig',
                'genero': 'Romance',
                'sinopsis': 'Una historia de amor que trasciende el tiempo.',
                'anio': 2025,
                'en_cartelera': True,
                'destacada': False
            },
            {
                'titulo': 'Risa en la Noche',
                'duracion': timedelta(minutes=95),
                'director': 'Taika Waititi',
                'genero': 'Comedia',
                'sinopsis': 'Comedia ligera y divertida para toda la familia.',
                'anio': 2025,
                'en_cartelera': True,
                'destacada': False
            },
            # Pelculas no en cartelera (15-20)
            {
                'titulo': 'Barbie',
                'duracion': timedelta(minutes=114),
                'director': 'Greta Gerwig',
                'genero': 'Comedia',
                'sinopsis': 'La mueca ms icnica llega al cine en una aventura rosa.',
                'anio': 2023,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Killers of the Flower Moon',
                'duracion': timedelta(minutes=206),
                'director': 'Martin Scorsese',
                'genero': 'Drama',
                'sinopsis': 'Drama histrico sobre crmenes y conspiracin.',
                'anio': 2023,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'The Zone of Interest',
                'duracion': timedelta(minutes=105),
                'director': 'Jonathan Glazer',
                'genero': 'Drama',
                'sinopsis': 'Drama histrico perturbador.',
                'anio': 2023,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Past Lives',
                'duracion': timedelta(minutes=115),
                'director': 'Celine Song',
                'genero': 'Romance',
                'sinopsis': 'Historia de amor y destino a travs de vidas pasadas.',
                'anio': 2023,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'American Fiction',
                'duracion': timedelta(minutes=117),
                'director': 'Cord Jefferson',
                'genero': 'Comedia',
                'sinopsis': 'Stira sobre la industria de publicacin en EE.UU.',
                'anio': 2023,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'The Iron Claw',
                'duracion': timedelta(minutes=160),
                'director': 'Sean Durkin',
                'genero': 'Drama',
                'sinopsis': 'Historia de la familia Von Erich en la lucha libre.',
                'anio': 2023,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Saltburn',
                'duracion': timedelta(minutes=131),
                'director': 'Emerald Fennell',
                'genero': 'Thriller',
                'sinopsis': 'Thriller oscuro sobre obsesin y seduccin.',
                'anio': 2023,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'The Brutalist',
                'duracion': timedelta(minutes=215),
                'director': 'Brady Corbet',
                'genero': 'Drama',
                'sinopsis': 'Epopeya sobre un arquitecto y su sueo americano.',
                'anio': 2023,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Godzilla Minus One',
                'duracion': timedelta(minutes=125),
                'director': 'Takashi Yamazaki',
                'genero': 'Ciencia Ficcin',
                'sinopsis': 'Versin japonesa reimaginada de Godzilla.',
                'anio': 2023,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'The Thousand Autumns',
                'duracion': timedelta(minutes=138),
                'director': 'Wong Kar-wai',
                'genero': 'Drama',
                'sinopsis': 'Drama pico en la China antigua.',
                'anio': 2024,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Inside Out 2',
                'duracion': timedelta(minutes=96),
                'director': 'Kelsey Mann',
                'genero': 'Animacin',
                'sinopsis': 'Las emociones regresan en una nueva aventura.',
                'anio': 2024,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Dune',
                'duracion': timedelta(minutes=156),
                'director': 'Denis Villeneuve',
                'genero': 'Ciencia Ficcin',
                'sinopsis': 'La primera parte de la adaptacin de la novela clsica.',
                'anio': 2021,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'The Shawshank Redemption',
                'duracion': timedelta(minutes=142),
                'director': 'Frank Darabont',
                'genero': 'Drama',
                'sinopsis': 'Un clsico del cine sobre amistad y redencin.',
                'anio': 1994,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Pulp Fiction',
                'duracion': timedelta(minutes=154),
                'director': 'Quentin Tarantino',
                'genero': 'Thriller',
                'sinopsis': 'Obras maestras del cine de los 90s.',
                'anio': 1994,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Inception',
                'duracion': timedelta(minutes=148),
                'director': 'Christopher Nolan',
                'genero': 'Ciencia Ficcin',
                'sinopsis': 'Thriller de ciencia ficcin sobre sueos y realidad.',
                'anio': 2010,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'The Dark Knight',
                'duracion': timedelta(minutes=152),
                'director': 'Christopher Nolan',
                'genero': 'Accin',
                'sinopsis': 'La segunda pelcula de la triloga del Caballero Oscuro.',
                'anio': 2008,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Interstellar',
                'duracion': timedelta(minutes=169),
                'director': 'Christopher Nolan',
                'genero': 'Ciencia Ficcin',
                'sinopsis': 'Epopeya del espacio sobre la supervivencia humana.',
                'anio': 2014,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Parasite',
                'duracion': timedelta(minutes=132),
                'director': 'Bong Joon-ho',
                'genero': 'Thriller',
                'sinopsis': 'Thriller surcoreano sobre clase social y manipulacin.',
                'anio': 2019,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Neon Genesis Evangelion',
                'duracion': timedelta(minutes=110),
                'director': 'Hideaki Anno',
                'genero': 'Animacin',
                'sinopsis': 'Adaptacin del anime de culto.',
                'anio': 2020,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'La Haine',
                'duracion': timedelta(minutes=98),
                'director': 'Mathieu Kassovitz',
                'genero': 'Drama',
                'sinopsis': 'Clsico francs sobre tensin racial y violencia.',
                'anio': 1995,
                'en_cartelera': False,
                'destacada': False
            },
            {
                'titulo': 'Mulholland Drive',
                'duracion': timedelta(minutes=147),
                'director': 'David Lynch',
                'genero': 'Thriller',
                'sinopsis': 'Misterio y realidad se entrelazan en Los ngeles.',
                'anio': 2001,
                'en_cartelera': False,
                'destacada': False
            },
        ]

        peliculas_creadas = []
        for pelicula_data in peliculas_data:
            genero = generos.get(pelicula_data.pop('genero'))
            director = directores.get(pelicula_data.pop('director'))
            en_cartelera = pelicula_data.pop('en_cartelera')
            destacada = pelicula_data.pop('destacada')

            pelicula, created = Peliculas.objects.get_or_create(
                titulo=pelicula_data['titulo'],
                defaults={
                    'duracion': pelicula_data['duracion'],
                    'director': director,
                    'genero': genero,
                    'sinopsis': pelicula_data['sinopsis'],
                    'anio': pelicula_data['anio'],
                }
            )
            peliculas_creadas.append(pelicula)

            # Crear/actualizar detalles
            DetallePelicula.objects.update_or_create(
                pelicula=pelicula,
                defaults={
                    'en_cartelera': en_cartelera,
                    'destacada': destacada,
                    'fecha_estreno': datetime(pelicula_data['anio'], 1, 1).date(),
                    'clasificacion': random.choice(['TP', '7', '12', '16', '18'])
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f' Pelcula: {pelicula.titulo}'))

        # Crear sesiones para pelculas en cartelera
        print("\n Creando sesiones...")
        salas = Sala.objects.all()
        if not salas.exists():
            self.stdout.write(self.style.WARNING(' No hay salas. Creando salas de prueba...'))
            for i in range(1, 6):
                Sala.objects.create(
                    identificador=f'Sala {i}',
                    capacidad=100 + (i * 20),
                    tiempo_max=240,
                    tipo=random.choice(['2D', '3D', 'IMAX', 'LASER'])
                )
            salas = Sala.objects.all()

        # Crear sesiones para pelculas en cartelera
        peliculas_cartelera = Peliculas.objects.filter(detalles__en_cartelera=True)
        base_time = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)

        sesiones_creadas = 0
        for pelicula in peliculas_cartelera:
            # 3-4 sesiones por pelcula
            for dia_offset in range(7):  # 7 das
                for hora_offset in range(random.randint(3, 4)):  # 3-4 sesiones por da
                    sala = random.choice(salas)
                    horario = base_time + timedelta(days=dia_offset, hours=10 + (hora_offset * 4))

                    sesion, created = Sesion.objects.get_or_create(
                        pelicula=pelicula,
                        sala=sala,
                        horario=horario
                    )
                    if created:
                        sesiones_creadas += 1

        self.stdout.write(self.style.SUCCESS(f' {sesiones_creadas} sesiones creadas'))

        # Resumen
        print("\n" + "="*50)
        print(" CARGA DE DATOS COMPLETADA")
        print("="*50)
        print(f" Estadsticas:")
        print(f"  - Gneros: {Genero.objects.count()}")
        print(f"  - Directores: {Director.objects.count()}")
        print(f"  - Pelculas: {Peliculas.objects.count()}")
        print(f"  - Pelculas en cartelera: {Peliculas.objects.filter(detalles__en_cartelera=True).count()}")
        print(f"  - Salas: {Sala.objects.count()}")
        print(f"  - Sesiones: {Sesion.objects.count()}")
        print("="*50)
