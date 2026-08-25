"""Tests de la cartelera: sesiones, programación automática y gestión."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cartelera import programacion
from cartelera.models import Sala, Sesion
from peliculas.models import DetallePelicula, Director, Genero, Peliculas


class BaseCartelera(TestCase):
    """Cine de prueba: dos salas y tres peliculas."""

    @classmethod
    def setUpTestData(cls):
        """Prepara los datos que comparten todos los tests de la clase."""
        cls.director = Director.objects.create(nombre="Denis Villeneuve")
        cls.genero = Genero.objects.create(nombre="Ciencia ficción")

        cls.sala = Sala.objects.create(
            identificador="Sala 1", capacidad=100, tiempo_max=240,
            tipo="2D", precio_entrada=Decimal("8.00"), filas=10, columnas=10)
        cls.otra_sala = Sala.objects.create(
            identificador="Sala 2", capacidad=80, tiempo_max=240,
            tipo="IMAX", precio_entrada=Decimal("12.00"), filas=8, columnas=10)

        cls.corta = cls.crear_pelicula("Peli corta", minutos=90)
        cls.larga = cls.crear_pelicula("Peli larga", minutos=180)
        cls.archivada = cls.crear_pelicula("Peli archivada", en_cartelera=False)

    @classmethod
    def crear_pelicula(cls, titulo, minutos=120, en_cartelera=True, puntuacion=0):
        """Crea una pelicula con su detalle, lista para usar en los tests."""
        pelicula = Peliculas.objects.create(
            titulo=titulo, duracion=timedelta(minutes=minutos),
            director=cls.director, genero=cls.genero,
            sinopsis="Sinopsis de prueba", anio=2030, puntuacion=puntuacion)
        DetallePelicula.objects.create(
            pelicula=pelicula, fecha_estreno="2030-01-01",
            en_cartelera=en_cartelera)
        return pelicula

    @staticmethod
    def momento(dia=10, hora=17, minuto=0):
        """Devuelve una fecha concreta de 2030, para no depender del dia de hoy."""
        return timezone.make_aware(timezone.datetime(2030, 6, dia, hora, minuto))


class TestSesion(BaseCartelera):
    """Cuánto ocupa una sesión y cuándo se considera que se solapa."""

    def test_la_sala_se_ocupa_publicidad_pelicula_y_limpieza(self):
        sesion = Sesion.objects.create(
            pelicula=self.corta, sala=self.sala, horario=self.momento())

        # 15 de publicidad + 90 de película + 20 de limpieza
        self.assertEqual(sesion.duracion_total_ocupacion, 125)
        self.assertEqual(sesion.hora_inicio_pelicula,
                         sesion.horario + timedelta(minutes=15))
        self.assertEqual(sesion.hora_fin_limpieza,
                         sesion.horario + timedelta(minutes=125))

    def test_no_se_admiten_dos_sesiones_pisandose_en_la_misma_sala(self):
        Sesion.objects.create(pelicula=self.larga, sala=self.sala,
                              horario=self.momento(hora=17))

        # La larga ocupa hasta las 20:35; a las 19:00 todavía no ha terminado
        chocan = Sesion(pelicula=self.corta, sala=self.sala,
                        horario=self.momento(hora=19))

        with self.assertRaises(ValidationError):
            chocan.clean()

    def test_si_da_tiempo_la_sesion_es_valida(self):
        Sesion.objects.create(pelicula=self.corta, sala=self.sala,
                              horario=self.momento(hora=17))

        # La corta libera la sala a las 19:05
        siguiente = Sesion(pelicula=self.corta, sala=self.sala,
                           horario=self.momento(hora=19, minuto=30))
        siguiente.clean()   # no debe lanzar

    def test_otra_sala_a_la_misma_hora_no_estorba(self):
        Sesion.objects.create(pelicula=self.larga, sala=self.sala,
                              horario=self.momento(hora=17))

        Sesion(pelicula=self.larga, sala=self.otra_sala,
               horario=self.momento(hora=17)).clean()


class TestProgramacion(BaseCartelera):
    """Las reglas de generación automática de la programación."""

    def test_entre_semana_no_se_abre_antes_de_las_cinco(self):
        for dia in range(0, 5):          # lunes a viernes
            horas = [h for h, _ in programacion.HORARIOS_POR_DIA[dia]]
            de_dia = [h for h in horas if h >= programacion.FIN_DE_LA_MADRUGADA]
            self.assertGreaterEqual(min(de_dia), 17,
                                    "el día %s abre antes de las 17:00" % dia)

    def test_solo_hay_matinal_el_fin_de_semana(self):
        for dia in (5, 6):
            horas = [h for h, _ in programacion.HORARIOS_POR_DIA[dia]]
            self.assertIn(12, horas)

    def test_el_ultimo_pase_de_viernes_y_sabado_es_a_la_una(self):
        for dia in (4, 5):
            horas = [h for h, _ in programacion.HORARIOS_POR_DIA[dia]]
            self.assertIn(1, horas)

        # El resto de días no tienen pase de madrugada
        for dia in (0, 1, 2, 3, 6):
            horas = [h for h, _ in programacion.HORARIOS_POR_DIA[dia]]
            self.assertFalse([h for h in horas if programacion.es_madrugada(h)])

    def test_en_madrugada_no_caben_peliculas_de_mas_de_dos_horas(self):
        self.assertTrue(programacion.cabe_en_la_franja(self.corta, 1))
        self.assertFalse(programacion.cabe_en_la_franja(self.larga, 1))
        # A otras horas sí
        self.assertTrue(programacion.cabe_en_la_franja(self.larga, 19))

    def test_el_pase_de_madrugada_cae_en_el_dia_siguiente(self):
        viernes = date(2030, 6, 14)
        pase = programacion.momento_del_pase(viernes, 1, 0)

        self.assertEqual(timezone.localtime(pase).date(), date(2030, 6, 15))
        self.assertEqual(timezone.localtime(pase).hour, 1)

    def test_las_horas_son_locales_y_no_utc(self):
        """Con timezone.now().replace(hour=17) saldrían las 19:00 en Madrid."""
        pase = programacion.momento_del_pase(date(2030, 6, 10), 17, 0)
        self.assertEqual(timezone.localtime(pase).hour, 17)

    def test_la_programacion_generada_no_tiene_solapamientos(self):
        sesiones, _ = programacion.generar(
            [self.corta, self.larga], [self.sala, self.otra_sala],
            dias=7, desde=date(2030, 6, 10))

        por_sala = {}
        for sesion in sesiones:
            por_sala.setdefault(sesion.sala_id, []).append(sesion)

        for lista in por_sala.values():
            lista.sort(key=lambda s: s.horario)
            for anterior, siguiente in zip(lista, lista[1:]):
                self.assertGreaterEqual(
                    siguiente.horario, anterior.hora_fin_limpieza,
                    "la sala sigue ocupada cuando empieza el siguiente pase")

    def test_todas_las_peliculas_entran_en_la_programacion(self):
        sesiones, _ = programacion.generar(
            [self.corta, self.larga], [self.sala, self.otra_sala],
            dias=7, desde=date(2030, 6, 10))

        programadas = {s.pelicula_id for s in sesiones}
        self.assertEqual(programadas, {self.corta.id, self.larga.id})

    def test_ninguna_pelicula_larga_acaba_en_la_madrugada(self):
        sesiones, _ = programacion.generar(
            [self.corta, self.larga], [self.sala, self.otra_sala],
            dias=14, desde=date(2030, 6, 10))

        for sesion in sesiones:
            if programacion.es_madrugada(timezone.localtime(sesion.horario).hour):
                self.assertLessEqual(sesion.pelicula.duracion,
                                     programacion.DURACION_MAXIMA_MADRUGADA)

    def test_se_respeta_lo_que_ya_estaba_programado(self):
        ocupado = self.momento(hora=17)
        previa = Sesion(pelicula=self.larga, sala=self.sala, horario=ocupado)

        sesiones, _ = programacion.generar(
            [self.corta], [self.sala], dias=1, desde=date(2030, 6, 10),
            ocupacion_previa={self.sala.id: [(ocupado, previa.hora_fin_limpieza)]})

        for sesion in sesiones:
            self.assertFalse(
                sesion.horario < previa.hora_fin_limpieza
                and ocupado < sesion.hora_fin_limpieza,
                "se ha programado encima de una sesión que ya existía")


class TestGestionDeSesiones(BaseCartelera):
    """La pantalla de gestión: acceso, filtros y alta manual."""

    @classmethod
    def setUpTestData(cls):
        """Prepara los datos que comparten todos los tests de la clase."""
        super().setUpTestData()
        cls.gestor = User.objects.create_user("gestor", password="clave")
        cls.gestor.groups.add(Group.objects.create(name="Gestores"))

        # Dos sesiones en días y salas distintas, para poder filtrar
        cls.sesion_hoy = Sesion.objects.create(
            pelicula=cls.corta, sala=cls.sala, horario=cls.momento(dia=10))
        cls.sesion_manana = Sesion.objects.create(
            pelicula=cls.larga, sala=cls.otra_sala, horario=cls.momento(dia=11))

    def setUp(self):
        """Deja la sesion iniciada como gestor antes de cada test."""
        self.client.force_login(self.gestor)

    def test_un_visitante_no_entra_en_la_gestion(self):
        self.client.logout()
        respuesta = self.client.get(reverse("sesiones_lista"))
        self.assertEqual(respuesta.status_code, 302)

    def test_sin_filtros_salen_todas(self):
        respuesta = self.client.get(reverse("sesiones_lista"))
        self.assertEqual(respuesta.context["total"], 2)

    def test_filtrar_por_pelicula(self):
        respuesta = self.client.get(reverse("sesiones_lista"),
                                    {"pelicula": self.corta.id})

        self.assertEqual(respuesta.context["total"], 1)
        self.assertEqual(respuesta.context["sesiones"][0], self.sesion_hoy)

    def test_filtrar_por_sala(self):
        respuesta = self.client.get(reverse("sesiones_lista"),
                                    {"sala": self.otra_sala.id})

        self.assertEqual(respuesta.context["total"], 1)
        self.assertEqual(respuesta.context["sesiones"][0], self.sesion_manana)

    def test_filtrar_por_fechas(self):
        respuesta = self.client.get(reverse("sesiones_lista"),
                                    {"desde": "2030-06-11"})
        self.assertEqual(respuesta.context["total"], 1)

        respuesta = self.client.get(reverse("sesiones_lista"),
                                    {"hasta": "2030-06-10"})
        self.assertEqual(respuesta.context["total"], 1)

    def test_una_fecha_invalida_se_ignora(self):
        respuesta = self.client.get(reverse("sesiones_lista"),
                                    {"desde": "no-es-una-fecha"})

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["total"], 2)

    def test_alta_manual_de_una_sesion(self):
        respuesta = self.client.post(reverse("sesion_form"), {
            "pelicula": self.corta.id,
            "sala": self.sala.id,
            "horario": "2030-07-01T20:00",
        })

        self.assertRedirects(respuesta, reverse("sesiones_lista"))
        self.assertTrue(Sesion.objects.filter(
            sala=self.sala, horario__date=date(2030, 7, 1)).exists())

    def test_el_alta_rechaza_una_sesion_que_se_solapa(self):
        antes = Sesion.objects.count()

        respuesta = self.client.post(reverse("sesion_form"), {
            "pelicula": self.corta.id,
            "sala": self.sala.id,
            "horario": "2030-06-10T18:00",   # la de las 17:00 sigue en marcha
        })

        self.assertEqual(respuesta.status_code, 200, "vuelve al formulario")
        self.assertEqual(Sesion.objects.count(), antes)
        self.assertContains(respuesta, "solapamiento")

    def test_al_editar_el_horario_viene_relleno(self):
        """El input datetime-local solo entiende AAAA-MM-DDTHH:MM."""
        respuesta = self.client.get(
            reverse("editar_sesion", args=[self.sesion_hoy.pk]))

        self.assertContains(respuesta, 'value="2030-06-10T17:00"')


class TestCarteleraPublica(BaseCartelera):
    """Lo que ve el visitante: cartelera y próximos estrenos."""

    def test_la_cartelera_se_divide_en_dos_secciones(self):
        respuesta = self.client.get(reverse("cartelera"))

        en_cartelera = list(respuesta.context["cartelera"])
        proximos = list(respuesta.context["proximos"])

        self.assertIn(self.corta, en_cartelera)
        self.assertIn(self.archivada, proximos)
        self.assertNotIn(self.archivada, en_cartelera)

    def test_los_proximos_estrenos_van_por_puntuacion(self):
        self.crear_pelicula("Mala", en_cartelera=False, puntuacion=5)
        self.crear_pelicula("Buena", en_cartelera=False, puntuacion=9)

        respuesta = self.client.get(reverse("cartelera"))
        notas = [p.puntuacion for p in respuesta.context["proximos"]]

        self.assertEqual(notas, sorted(notas, reverse=True))

    def test_el_detalle_agrupa_las_sesiones_por_sala(self):
        Sesion.objects.create(pelicula=self.corta, sala=self.sala,
                              horario=self.momento(hora=17))
        Sesion.objects.create(pelicula=self.corta, sala=self.sala,
                              horario=self.momento(hora=20))

        respuesta = self.client.get(
            reverse("detalle_cartelera", args=[self.corta.pk]),
            {"fecha": "2030-06-10"})

        salas = dict(respuesta.context["salas_con_sesiones"])
        self.assertEqual(len(salas), 1, "las dos sesiones van en la misma sala")
        self.assertEqual(len(salas[self.sala]), 2)
