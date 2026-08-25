"""Tests de películas: carteles guardados en la BBDD y ficha desde TMDB."""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from peliculas import tmdb
from peliculas.models import (CartelPelicula, DetallePelicula, Director,
                              Genero, Peliculas)

# Un JPEG mínimo válido, para no depender de ficheros de disco
JPEG = bytes.fromhex(
    "ffd8ffe000104a46494600010100000100010000ffdb004300"
    + "08" * 64 +
    "ffc2000b080001000101011100ffc40014000100000000000000000000000000000009"
    "ffda0008010100000001d2cf20ffd9")


class BasePeliculas(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.director = Director.objects.create(nombre="Greta Gerwig")
        cls.genero = Genero.objects.create(nombre="Comedia")
        cls.pelicula = Peliculas.objects.create(
            titulo="Barbie", duracion=timedelta(minutes=114),
            director=cls.director, genero=cls.genero,
            sinopsis="Sinopsis de prueba", anio=2023)
        DetallePelicula.objects.create(
            pelicula=cls.pelicula, fecha_estreno="2023-07-19", en_cartelera=True)


class TestCartelEnBBDD(BasePeliculas):
    """El cartel se guarda en la base de datos porque `media/` no se comparte."""

    def test_guardar_cartel_lo_deja_en_la_bbdd(self):
        self.pelicula.guardar_cartel(JPEG, "barbie.jpg")

        cartel = CartelPelicula.objects.get(pelicula=self.pelicula)
        self.assertEqual(bytes(cartel.datos), JPEG)
        self.assertEqual(cartel.tipo, "image/jpeg")

    def test_el_cartel_se_sirve_por_su_url(self):
        self.pelicula.guardar_cartel(JPEG, "barbie.jpg")
        self.pelicula.save()

        respuesta = self.client.get(
            reverse("cartel_pelicula", args=[self.pelicula.pk]))

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "image/jpeg")
        self.assertEqual(respuesta.content, JPEG)

    def test_el_cartel_se_cachea(self):
        self.pelicula.guardar_cartel(JPEG, "barbie.jpg")
        self.pelicula.save()

        respuesta = self.client.get(
            reverse("cartel_pelicula", args=[self.pelicula.pk]))

        self.assertIn("max-age", respuesta.get("Cache-Control", ""))

    def test_sin_cartel_da_404(self):
        respuesta = self.client.get(
            reverse("cartel_pelicula", args=[self.pelicula.pk]))
        self.assertEqual(respuesta.status_code, 404)

    def test_url_cartel_apunta_a_la_vista(self):
        self.pelicula.guardar_cartel(JPEG, "barbie.jpg")
        self.pelicula.save()

        self.assertEqual(
            self.pelicula.url_cartel,
            reverse("cartel_pelicula", args=[self.pelicula.pk]))

    def test_sin_imagen_no_hay_url(self):
        self.assertIsNone(self.pelicula.url_cartel)

    def test_borrar_la_pelicula_se_lleva_el_cartel(self):
        self.pelicula.guardar_cartel(JPEG, "barbie.jpg")
        self.pelicula.save()

        self.pelicula.delete()
        self.assertEqual(CartelPelicula.objects.count(), 0)

    def test_volver_a_guardar_sustituye_el_cartel(self):
        self.pelicula.guardar_cartel(JPEG, "barbie.jpg")
        self.pelicula.guardar_cartel(JPEG + b"\x00", "barbie.jpg")

        self.assertEqual(CartelPelicula.objects.filter(
            pelicula=self.pelicula).count(), 1)


class TestBuscarEnTMDB(BasePeliculas):
    """El botón "Buscar en TMDB" del alta de película.

    No se llama a la API de verdad: se sustituye la respuesta.
    """

    FICHA = {
        "titulo": "Interstellar",
        "sinopsis": "Un grupo de exploradores cruza un agujero de gusano.",
        "duracion": 169,
        "anio": 2014,
        "estreno": "2014-11-05",
        "director": "Christopher Nolan",
        "genero": "Aventura",
        "poster": "/poster.jpg",
        "puntuacion": 8.5,
    }

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.gestor = User.objects.create_user("gestor", password="clave")
        cls.gestor.groups.add(Group.objects.create(name="Gestores"))

    def setUp(self):
        self.client.force_login(self.gestor)

    def test_un_visitante_no_puede_buscar(self):
        self.client.logout()
        respuesta = self.client.get(reverse("buscar_tmdb"),
                                    {"titulo": "Interstellar"})
        self.assertEqual(respuesta.status_code, 302)

    @patch("peliculas.views.tmdb.buscar")
    def test_devuelve_la_ficha_en_json(self, buscar):
        buscar.return_value = self.FICHA

        respuesta = self.client.get(reverse("buscar_tmdb"),
                                    {"titulo": "Interstellar"})
        datos = respuesta.json()

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(datos["titulo"], "Interstellar")
        self.assertEqual(datos["duracion"], 169)
        self.assertEqual(datos["puntuacion"], 8.5)

    @patch("peliculas.views.tmdb.buscar")
    def test_crea_el_director_y_el_genero_si_no_existen(self, buscar):
        buscar.return_value = self.FICHA

        datos = self.client.get(reverse("buscar_tmdb"),
                                {"titulo": "Interstellar"}).json()

        self.assertTrue(Director.objects.filter(nombre="Christopher Nolan").exists())
        self.assertIsNotNone(datos["director"]["id"],
                             "el desplegable necesita el id, no solo el nombre")

    @patch("peliculas.views.tmdb.buscar")
    def test_reutiliza_el_genero_aunque_cambie_la_mayuscula(self, buscar):
        Genero.objects.create(nombre="AVENTURA")
        buscar.return_value = self.FICHA

        self.client.get(reverse("buscar_tmdb"), {"titulo": "Interstellar"})

        self.assertEqual(Genero.objects.filter(nombre__iexact="aventura").count(), 1,
                         "no debe duplicarse el género por la capitalización")

    def test_sin_titulo_avisa(self):
        respuesta = self.client.get(reverse("buscar_tmdb"), {"titulo": ""})

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("título", respuesta.json()["error"])

    @patch("peliculas.views.tmdb.buscar")
    def test_si_tmdb_no_la_encuentra_avisa(self, buscar):
        buscar.return_value = None

        respuesta = self.client.get(reverse("buscar_tmdb"), {"titulo": "zzzz"})

        self.assertEqual(respuesta.status_code, 404)

    @patch("peliculas.views.tmdb.buscar")
    def test_sin_clave_no_revienta(self, buscar):
        buscar.side_effect = tmdb.ErrorTMDB("No hay clave de TMDB.")

        respuesta = self.client.get(reverse("buscar_tmdb"),
                                    {"titulo": "Interstellar"})

        self.assertEqual(respuesta.status_code, 502,
                         "debe avisar, no dar un error 500")
        self.assertIn("clave", respuesta.json()["error"])

    @patch("peliculas.views.tmdb.hay_clave")
    def test_sin_clave_el_boton_no_aparece(self, hay_clave):
        hay_clave.return_value = False

        respuesta = self.client.get(reverse("nueva_pelicula"))

        self.assertNotContains(respuesta, 'id="tmdb-buscar"')

    @patch("peliculas.views.tmdb.hay_clave")
    def test_con_clave_el_boton_aparece(self, hay_clave):
        hay_clave.return_value = True

        respuesta = self.client.get(reverse("nueva_pelicula"))

        self.assertContains(respuesta, 'id="tmdb-buscar"')


class TestAltaDePelicula(BasePeliculas):
    """El alta guarda el cartel en la BBDD, venga de un fichero o de TMDB."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.gestor = User.objects.create_user("gestor", password="clave")
        cls.gestor.groups.add(Group.objects.create(name="Gestores"))

    def setUp(self):
        self.client.force_login(self.gestor)

    def datos(self, **extra):
        base = {
            "titulo": "Película nueva",
            "duracion": "1:30:00",
            "director": self.director.id,
            "genero": self.genero.id,
            "sinopsis": "Una sinopsis",
            "anio": 2030,
        }
        base.update(extra)
        return base

    def test_la_imagen_subida_va_tambien_a_la_bbdd(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.post(reverse("nueva_pelicula"), self.datos(
            imagen=SimpleUploadedFile("cartel.jpg", JPEG, content_type="image/jpeg")))

        nueva = Peliculas.objects.get(titulo="Película nueva")
        self.assertTrue(CartelPelicula.objects.filter(pelicula=nueva).exists())

    @patch("peliculas.views.tmdb.descargar_cartel")
    def test_el_cartel_de_tmdb_se_descarga_al_guardar(self, descargar):
        descargar.return_value = JPEG

        self.client.post(reverse("nueva_pelicula"),
                         self.datos(poster_tmdb="/poster.jpg",
                                    puntuacion_tmdb="7.5"))

        nueva = Peliculas.objects.get(titulo="Película nueva")
        self.assertTrue(CartelPelicula.objects.filter(pelicula=nueva).exists())
        self.assertEqual(nueva.puntuacion, Decimal("7.5"))

    @patch("peliculas.views.tmdb.descargar_cartel")
    def test_si_falla_la_descarga_la_pelicula_se_crea_igual(self, descargar):
        descargar.side_effect = tmdb.ErrorTMDB("sin conexión")

        respuesta = self.client.post(reverse("nueva_pelicula"),
                                     self.datos(poster_tmdb="/poster.jpg"),
                                     follow=True)

        self.assertTrue(Peliculas.objects.filter(titulo="Película nueva").exists())
        self.assertIn("cartel", " ".join(
            m.message for m in respuesta.context["messages"]))


class TestUtilidadesTMDB(TestCase):
    """Funciones sueltas del módulo, sin tocar la red."""

    def test_distingue_el_token_v4_de_la_clave_v3(self):
        self.assertTrue(tmdb.es_token_v4("eyJhbGciOi.eyJhdWQiOi.firma"))
        self.assertFalse(tmdb.es_token_v4("45bffcef7b6f49a374d22c97b7d27501"))

    def test_la_clave_v3_viaja_en_la_url_y_la_v4_no(self):
        v3 = tmdb.con_clave({}, "45bffcef7b6f49a374d22c97b7d27501")
        v4 = tmdb.con_clave({}, "eyJhbGciOi.eyJhdWQiOi.firma")

        self.assertIn("api_key", v3)
        self.assertNotIn("api_key", v4, "la v4 va en la cabecera Authorization")

    def test_la_sinopsis_se_recorta_por_palabra(self):
        largo = "palabra " * 60

        recortada = tmdb.recortar_sinopsis(largo)

        self.assertLessEqual(len(recortada), 300,
                             "el campo sinopsis es CharField(300)")
        self.assertTrue(recortada.endswith("..."))

    def test_una_sinopsis_corta_no_se_toca(self):
        self.assertEqual(tmdb.recortar_sinopsis("Corta"), "Corta")

    def test_el_slug_quita_acentos_y_espacios(self):
        self.assertEqual(tmdb.slug("El Caballero Oscuro"), "el-caballero-oscuro")
        self.assertEqual(tmdb.slug("Parásitos"), "parasitos")
