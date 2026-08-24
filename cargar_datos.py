#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import datetime, timedelta
from peliculas.models import Peliculas, Director, Genero, DetallePelicula
from cartelera.models import Sala, Sesion
import random

print("=== Cargando datos de prueba ===\n")

# Crear generos
print("[1/4] Creando generos...")
generos_data = [
    'Acción', 'Comedia', 'Drama', 'Ciencia Ficción',
    'Thriller', 'Aventura', 'Animación', 'Romance',
    'Terror', 'Fantasía'
]
generos = {}
for genero_nombre in generos_data:
    genero, created = Genero.objects.get_or_create(nombre=genero_nombre)
    generos[genero_nombre] = genero
    if created:
        print(f"  + Genero: {genero_nombre}")

# Crear directores
print("\n[2/4] Creando directores...")
directores_data = [
    'Christopher Nolan', 'Denis Villeneuve', 'Damien Chazelle',
    'Ari Aster', 'Greta Gerwig', 'Taika Waititi', 'James Gunn',
    'Wong Kar-wai', 'Yorgos Lanthimos', 'Paul Thomas Anderson',
    'Bong Joon-ho', 'Pedro Almodovar', 'Wes Anderson', 'David Fincher',
    'Robert Eggers', 'Jon M. Chu', 'Ridley Scott', 'Barry Jenkins',
    'Jeff Fowler', 'David Derrick Jr.', 'Julius Onah', 'Jeronimo Rodriguez',
    'Martin Scorsese', 'Frank Darabont', 'Quentin Tarantino',
    'James Cameron', 'David Lynch', 'Mathieu Kassovitz', 'Hideaki Anno',
    'Sean Durkin', 'Emerald Fennell', 'Brady Corbet', 'Takashi Yamazaki',
    'Kelsey Mann'
]
directores = {}
for director_nombre in directores_data:
    director, created = Director.objects.get_or_create(nombre=director_nombre)
    directores[director_nombre] = director
    if created:
        print(f"  + Director: {director_nombre}")

# Crear películas
print("\n[3/4] Creando peliculas...")
peliculas_data = [
    # En cartelera (14)
    ('Dune: Profecia', 166, 'Denis Villeneuve', 'Ciencia Ficción', 'La historia del ascenso de los Bene Gesserit', 2026, True, True),
    ('Oppenheimer 2', 180, 'Christopher Nolan', 'Drama', 'Continua la historia del padre de la bomba atomica', 2026, True, True),
    ('Avatar 4', 200, 'James Cameron', 'Ciencia Ficción', 'La saga continua en Pandora', 2026, True, True),
    ('Nosferatu', 132, 'Robert Eggers', 'Terror', 'Remake del clasico del cine gotico aleman', 2025, True, False),
    ('Wicked', 161, 'Jon M. Chu', 'Fantasía', 'La historia de la Bruja Malvada del Oeste', 2024, True, True),
    ('Gladiador II', 148, 'Ridley Scott', 'Acción', 'La venganza en la arena romana', 2024, True, True),
    ('Mufasa: El Rey Leon', 145, 'Barry Jenkins', 'Animación', 'La historia de origen del Rey Leon', 2024, True, False),
    ('Sonic 3', 104, 'Jeff Fowler', 'Acción', 'Sonic enfrenta su mayor desafio', 2024, True, False),
    ('Moana 2', 100, 'David Derrick Jr.', 'Animación', 'Moana regresa para una nueva aventura', 2024, True, False),
    ('Capitan America: Sentinela del Atlantico', 151, 'Julius Onah', 'Acción', 'El nuevo Capitan America', 2025, True, True),
    ('El Conde', 112, 'Jeronimo Rodriguez', 'Drama', 'Drama historico sobre la vida de un conde', 2025, True, False),
    ('Fantasia Invisible', 118, 'Ari Aster', 'Thriller', 'Un thriller psicologico', 2025, True, False),
    ('Crepusculo Eterno', 125, 'Greta Gerwig', 'Romance', 'Una historia de amor que trasciende', 2025, True, False),
    ('Risa en la Noche', 95, 'Taika Waititi', 'Comedia', 'Comedia para toda la familia', 2025, True, False),
    # No en cartelera (20)
    ('Barbie', 114, 'Greta Gerwig', 'Comedia', 'La muneca mas iconica en el cine', 2023, False, False),
    ('Killers of the Flower Moon', 206, 'Martin Scorsese', 'Drama', 'Drama historico sobre crimenes', 2023, False, False),
    ('The Zone of Interest', 105, 'Christopher Nolan', 'Drama', 'Drama historico perturbador', 2023, False, False),
    ('Past Lives', 115, 'Damien Chazelle', 'Romance', 'Historia de amor a traves de vidas pasadas', 2023, False, False),
    ('American Fiction', 117, 'David Fincher', 'Comedia', 'Satira sobre la industria de publicacion', 2023, False, False),
    ('The Iron Claw', 160, 'Sean Durkin', 'Drama', 'Historia de la familia Von Erich', 2023, False, False),
    ('Saltburn', 131, 'Emerald Fennell', 'Thriller', 'Thriller oscuro sobre obsesion', 2023, False, False),
    ('The Brutalist', 215, 'Brady Corbet', 'Drama', 'Epopeya sobre un arquitecto', 2023, False, False),
    ('Godzilla Minus One', 125, 'Takashi Yamazaki', 'Ciencia Ficción', 'Version japonesa reimaginada', 2023, False, False),
    ('The Thousand Autumns', 138, 'Wong Kar-wai', 'Drama', 'Drama epico en la China antigua', 2024, False, False),
    ('Inside Out 2', 96, 'Kelsey Mann', 'Animación', 'Las emociones regresan', 2024, False, False),
    ('Dune', 156, 'Denis Villeneuve', 'Ciencia Ficción', 'La primera parte de la adaptacion', 2021, False, False),
    ('The Shawshank Redemption', 142, 'Frank Darabont', 'Drama', 'Un clasico sobre amistad y redencion', 1994, False, False),
    ('Pulp Fiction', 154, 'Quentin Tarantino', 'Thriller', 'Obras maestras del cine', 1994, False, False),
    ('Inception', 148, 'Christopher Nolan', 'Ciencia Ficción', 'Thriller sobre suenos y realidad', 2010, False, False),
    ('The Dark Knight', 152, 'Christopher Nolan', 'Acción', 'La trilogia del Caballero Oscuro', 2008, False, False),
    ('Interstellar', 169, 'Christopher Nolan', 'Ciencia Ficción', 'Epopeya del espacio', 2014, False, False),
    ('Parasite', 132, 'Bong Joon-ho', 'Thriller', 'Thriller surcoreano sobre clase social', 2019, False, False),
    ('Neon Genesis Evangelion', 110, 'Hideaki Anno', 'Animación', 'Adaptacion del anime de culto', 2020, False, False),
    ('La Haine', 98, 'Mathieu Kassovitz', 'Drama', 'Clasico frances sobre tension racial', 1995, False, False),
    ('Mulholland Drive', 147, 'David Lynch', 'Thriller', 'Misterio y realidad en Los Angeles', 2001, False, False),
]

peliculas_creadas = []
for titulo, duracion_min, director_nombre, genero_nombre, sinopsis, anio, en_cartelera, destacada in peliculas_data:
    genero = generos.get(genero_nombre)
    director = directores.get(director_nombre)

    pelicula, created = Peliculas.objects.get_or_create(
        titulo=titulo,
        defaults={
            'duracion': timedelta(minutes=duracion_min),
            'director': director,
            'genero': genero,
            'sinopsis': sinopsis,
            'anio': anio,
        }
    )
    peliculas_creadas.append(pelicula)

    # Crear detalles
    DetallePelicula.objects.update_or_create(
        pelicula=pelicula,
        defaults={
            'en_cartelera': en_cartelera,
            'destacada': destacada,
            'fecha_estreno': datetime(anio, 1, 1).date(),
            'clasificacion': random.choice(['TP', '7', '12', '16', '18'])
        }
    )

    if created:
        print(f"  + Pelicula: {titulo}")

# Crear 7 salas reales con tipos especificos
print("\n[4/4] Creando salas y sesiones...")
salas_config = [
    ('Sala 1', 150, '2D'),
    ('Sala 2', 180, '3D'),
    ('Sala 3', 200, 'IMAX'),
    ('Sala 4', 200, 'IMAX'),
    ('Sala 5', 220, 'LASER'),
    ('Sala 6', 160, '4DX'),
    ('Sala 7', 120, 'VIP'),
]

salas = []
for identificador, capacidad, tipo in salas_config:
    sala, created = Sala.objects.get_or_create(
        identificador=identificador,
        defaults={
            'capacidad': capacidad,
            'tiempo_max': 240,
            'tipo': tipo
        }
    )
    salas.append(sala)
    if created:
        print(f"  + {sala.identificador} ({tipo}) - Capacidad: {capacidad}")

# Horarios por dia de la semana
# 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
horarios_por_dia = {
    0: [18, 20, 22],  # Lunes: 18, 20, 22
    1: [18, 20, 22],  # Martes: 18, 20, 22
    2: [18, 20, 22],  # Miercoles: 18, 20, 22
    3: [18, 20, 22],  # Jueves: 18, 20, 22
    4: [18, 20, 22, 0],  # Viernes: 18, 20, 22, 00
    5: [12, 18, 20, 22, 0],  # Sabado: 12, 18, 20, 22, 00
    6: [12, 14, 18, 20, 22, 0],  # Domingo: 12, 14, 18, 20, 22, 00
}

# Crear sesiones para peliculas en cartelera
# Distribuir peliculas en salas para que todas tengan contenido
peliculas_cartelera = list(Peliculas.objects.filter(detalles__en_cartelera=True))
base_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

sesiones_creadas = 0
for pelicula_idx, pelicula in enumerate(peliculas_cartelera):
    # Asignar 3-4 salas por película para que todas las salas tengan contenido
    salas_asignadas = []
    num_salas = min(4, len(salas))  # 3-4 salas por película

    # Distribuir round-robin para garantizar que todas las salas tengan películas
    for i in range(num_salas):
        sala_idx = (pelicula_idx * num_salas + i) % len(salas)
        salas_asignadas.append(salas[sala_idx])

    for dia_offset in range(14):  # 2 semanas
        fecha = base_time + timedelta(days=dia_offset)
        dia_semana = fecha.weekday()
        horas = horarios_por_dia[dia_semana]

        for hora in horas:
            sala = salas_asignadas[hora % len(salas_asignadas)]

            # Manejar medianoche (hora 0 = 00:00 del dia siguiente)
            if hora == 0:
                horario = fecha + timedelta(days=1, hours=0, minutes=random.randint(0, 30))
            else:
                horario = fecha.replace(hour=hora, minute=random.randint(0, 30))

            try:
                sesion, created = Sesion.objects.get_or_create(
                    pelicula=pelicula,
                    sala=sala,
                    horario=horario
                )
                if created:
                    sesiones_creadas += 1
            except:
                pass

# Resumen
print("\n" + "="*50)
print("CARGA COMPLETADA")
print("="*50)
print(f"Generos: {Genero.objects.count()}")
print(f"Directores: {Director.objects.count()}")
print(f"Peliculas: {Peliculas.objects.count()}")
print(f"Peliculas en cartelera: {Peliculas.objects.filter(detalles__en_cartelera=True).count()}")
print(f"Salas: {Sala.objects.count()}")
print(f"Sesiones: {Sesion.objects.count()}")
print("="*50)
