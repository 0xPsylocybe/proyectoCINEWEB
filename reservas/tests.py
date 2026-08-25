"""Tests de la compra de entradas: butacas, reservas y recaudación."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cartelera.models import Sala, Sesion
from peliculas.models import DetallePelicula, Director, Genero, Peliculas
from reservas import butacas as butacas_svc
from reservas.models import EntradaButaca, ReservaButaca, VentaEntrada
from restauracion.models import Categoria, Producto, VentaProducto


class BaseCine(TestCase):
    """Cine mínimo del que parten todos los tests: una sala, dos películas
    y una sesión. Las fechas van a 2030 para no chocar con la programación
    real ni depender del día en que se ejecuten."""

    @classmethod
    def setUpTestData(cls):
        cls.director = Director.objects.create(nombre="Christopher Nolan")
        cls.genero = Genero.objects.create(nombre="Ciencia ficción")

        cls.sala = Sala.objects.create(
            identificador="Sala 1", capacidad=100, tiempo_max=240,
            tipo="2D", precio_entrada=Decimal("8.00"), filas=10, columnas=10)

        cls.corta = cls.crear_pelicula("Peli corta", minutos=90)
        cls.larga = cls.crear_pelicula("Peli larga", minutos=180)

        cls.momento = timezone.make_aware(timezone.datetime(2030, 6, 10, 17, 0))
        cls.sesion = Sesion.objects.create(
            pelicula=cls.corta, sala=cls.sala, horario=cls.momento)

    @classmethod
    def crear_pelicula(cls, titulo, minutos=120, en_cartelera=True):
        pelicula = Peliculas.objects.create(
            titulo=titulo, duracion=timedelta(minutes=minutos),
            director=cls.director, genero=cls.genero,
            sinopsis="Sinopsis de prueba", anio=2030)
        DetallePelicula.objects.create(
            pelicula=pelicula, fecha_estreno="2030-01-01",
            en_cartelera=en_cartelera)
        return pelicula


class TestButacas(BaseCine):
    """La butaca no se puede vender dos veces, ni siquiera a la vez."""

    def comprar(self, cliente, butacas, productos=None):
        """Hace el recorrido completo: carrito -> confirmación -> compra."""
        datos = {"sesion": self.sesion.id, "butacas": butacas}
        datos.update(productos or {})
        cliente.post(reverse("reservas:carrito_pelicula",
                             args=[self.sesion.pelicula_id]), datos)
        return cliente.post(reverse("reservas:confirmacion_compra"))

    def test_el_mapa_tiene_una_butaca_por_asiento_de_la_sala(self):
        respuesta = self.client.get(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id})
        mapa = respuesta.context["mapa_butacas"]

        self.assertEqual(len(mapa["filas"]), self.sala.filas)
        self.assertEqual(len(mapa["filas"][0]["butacas"]), self.sala.columnas)

    def test_elegir_butacas_las_reserva_sin_venderlas(self):
        self.client.post(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id, "butacas": ["1-5", "1-6"]})

        self.assertEqual(ReservaButaca.objects.count(), 2)
        self.assertEqual(EntradaButaca.objects.count(), 0,
                         "no debe venderse nada hasta confirmar")

    def test_la_reserva_dura_treinta_minutos(self):
        self.client.post(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id, "butacas": ["1-5"]})

        reserva = ReservaButaca.objects.get()
        minutos = (reserva.expira_en - timezone.now()).total_seconds() / 60
        self.assertAlmostEqual(minutos, 30, delta=1)

    def test_otro_comprador_no_ve_libre_una_butaca_reservada(self):
        self.client.post(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id, "butacas": ["1-5"]})

        otro = self.client_class()
        respuesta = otro.get(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id})

        estados = {(b["fila"], b["numero"]): b["estado"]
                   for fila in respuesta.context["mapa_butacas"]["filas"]
                   for b in fila["butacas"]}
        self.assertEqual(estados[(1, 5)], "ocupada")

    def test_dos_compradores_no_pueden_llevarse_la_misma_butaca(self):
        ana, bob = self.client_class(), self.client_class()
        self.comprar(ana, ["1-5"])

        respuesta = bob.post(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id, "butacas": ["1-5"]}, follow=True)

        self.assertEqual(
            EntradaButaca.objects.filter(sesion=self.sesion, fila=1, numero=5).count(),
            1, "la butaca solo puede estar vendida una vez")
        self.assertIn("adelantó", " ".join(
            m.message for m in respuesta.context["messages"]))

    def test_la_base_de_datos_impide_la_doble_venta(self):
        """Aunque alguien se salte la aplicación, la restricción está en la BBDD."""
        from django.db import IntegrityError

        venta = VentaEntrada.objects.create(
            sesion=self.sesion, cantidad=1,
            precio_unitario=Decimal("8.00"), total_venta=Decimal("8.00"))
        EntradaButaca.objects.create(venta=venta, sesion=self.sesion,
                                     fila=3, numero=3)

        with self.assertRaises(IntegrityError):
            EntradaButaca.objects.create(venta=venta, sesion=self.sesion,
                                         fila=3, numero=3)

    def test_una_reserva_caducada_libera_la_butaca(self):
        self.client.post(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id, "butacas": ["2-2"]})

        # Se simula que han pasado los 30 minutos
        ReservaButaca.objects.update(expira_en=timezone.now() - timedelta(seconds=1))

        otro = self.client_class()
        respuesta = otro.get(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id})

        estados = {(b["fila"], b["numero"]): b["estado"]
                   for fila in respuesta.context["mapa_butacas"]["filas"]
                   for b in fila["butacas"]}
        self.assertEqual(estados[(2, 2)], "libre")
        self.assertFalse(ReservaButaca.objects.exists(),
                         "las caducadas se borran al consultar el mapa")

    def test_confirmar_con_la_reserva_caducada_no_vende(self):
        self.client.post(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id, "butacas": ["4-4"]})
        ReservaButaca.objects.update(expira_en=timezone.now() - timedelta(seconds=1))

        respuesta = self.client.get(reverse("reservas:confirmacion_compra"),
                                    follow=True)

        self.assertEqual(VentaEntrada.objects.count(), 0)
        self.assertIn("caducado", " ".join(
            m.message for m in respuesta.context["messages"]))

    def test_hay_que_elegir_alguna_butaca(self):
        respuesta = self.client.post(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id, "butacas": []}, follow=True)

        self.assertEqual(ReservaButaca.objects.count(), 0)
        self.assertIn("al menos una butaca", " ".join(
            m.message for m in respuesta.context["messages"]))


class TestCompra(BaseCine):
    """El recorrido completo y lo que queda guardado."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.categoria = Categoria.objects.create(nombre="Bebidas")
        cls.producto = Producto.objects.create(
            nombre="Refresco", precio=Decimal("3.50"), categoria=cls.categoria)

    def comprar(self, butacas, productos=None):
        datos = {"sesion": self.sesion.id, "butacas": butacas}
        datos.update(productos or {})
        self.client.post(reverse("reservas:carrito_pelicula",
                                 args=[self.sesion.pelicula_id]), datos)
        return self.client.post(reverse("reservas:confirmacion_compra"))

    def test_una_entrada_por_butaca(self):
        self.comprar(["1-1", "1-2", "1-3"])

        venta = VentaEntrada.objects.get()
        self.assertEqual(venta.cantidad, 3)
        self.assertEqual(venta.butacas.count(), 3)

    def test_el_precio_lo_pone_la_sala(self):
        self.comprar(["1-1", "1-2"])

        venta = VentaEntrada.objects.get()
        self.assertEqual(venta.precio_unitario, self.sala.precio_entrada)
        self.assertEqual(venta.total_venta, self.sala.precio_entrada * 2)

    def test_se_pueden_anadir_productos_a_la_compra(self):
        self.comprar(["1-1"], {"producto_%s" % self.producto.id: 2})

        venta_producto = VentaProducto.objects.get()
        self.assertEqual(venta_producto.cantidad, 2)
        self.assertEqual(venta_producto.total_venta, self.producto.precio * 2)

    def test_el_resguardo_muestra_lo_comprado(self):
        self.comprar(["1-1", "1-2"], {"producto_%s" % self.producto.id: 1})

        respuesta = self.client.get(reverse("reservas:compra_exitosa"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.corta.titulo)
        self.assertContains(respuesta, self.sala.identificador)
        self.assertContains(respuesta, "A1")
        self.assertContains(respuesta, self.producto.nombre)
        esperado = self.sala.precio_entrada * 2 + self.producto.precio
        self.assertEqual(respuesta.context["total"], esperado)

    def test_el_resguardo_aguanta_una_recarga(self):
        self.comprar(["1-1"])
        self.client.get(reverse("reservas:compra_exitosa"))

        segunda = self.client.get(reverse("reservas:compra_exitosa"))
        self.assertEqual(segunda.status_code, 200)

    def test_sin_compra_previa_no_hay_resguardo(self):
        respuesta = self.client.get(reverse("reservas:compra_exitosa"))
        self.assertRedirects(respuesta, reverse("cartelera"))

    def test_la_venta_necesita_una_sesion(self):
        """Una entrada sin sesión no identifica película, sala ni horario."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            VentaEntrada.objects.create(
                sesion=None, cantidad=1,
                precio_unitario=Decimal("8.00"), total_venta=Decimal("8.00"))


class TestRecaudacion(BaseCine):
    """El trigger que mantiene al día `Peliculas.recaudacion`."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.otra_sesion = Sesion.objects.create(
            pelicula=cls.larga, sala=cls.sala,
            horario=cls.momento + timedelta(days=1))

    def recaudacion(self, pelicula):
        return Peliculas.objects.get(pk=pelicula.pk).recaudacion

    def vender(self, sesion, importe):
        return VentaEntrada.objects.create(
            sesion=sesion, cantidad=1,
            precio_unitario=Decimal(importe), total_venta=Decimal(importe))

    def test_una_venta_suma(self):
        self.vender(self.sesion, "20.00")
        self.assertEqual(self.recaudacion(self.corta), Decimal("20.00"))

    def test_una_anulacion_resta(self):
        venta = self.vender(self.sesion, "20.00")
        venta.delete()
        self.assertEqual(self.recaudacion(self.corta), Decimal("0.00"))

    def test_corregir_el_importe_ajusta_la_diferencia(self):
        venta = self.vender(self.sesion, "20.00")
        venta.total_venta = Decimal("35.00")
        venta.save()
        self.assertEqual(self.recaudacion(self.corta), Decimal("35.00"))

    def test_cambiar_de_pelicula_mueve_la_recaudacion(self):
        venta = self.vender(self.sesion, "20.00")

        venta.sesion = self.otra_sesion
        venta.save()

        self.assertEqual(self.recaudacion(self.corta), Decimal("0.00"))
        self.assertEqual(self.recaudacion(self.larga), Decimal("20.00"))

    def test_varias_ventas_se_acumulan(self):
        self.vender(self.sesion, "10.00")
        self.vender(self.sesion, "15.50")
        self.assertEqual(self.recaudacion(self.corta), Decimal("25.50"))

    def test_los_productos_no_cuentan_como_recaudacion(self):
        """La recaudación es taquilla; el Snack Bar va aparte."""
        categoria = Categoria.objects.create(nombre="Bebidas")
        producto = Producto.objects.create(
            nombre="Refresco", precio=Decimal("3.50"), categoria=categoria)

        VentaProducto.objects.create(producto=producto, cantidad=2,
                                     total_venta=Decimal("7.00"))

        self.assertEqual(self.recaudacion(self.corta), Decimal("0.00"))

    def test_la_compra_desde_la_web_actualiza_la_recaudacion(self):
        self.client.post(
            reverse("reservas:carrito_pelicula", args=[self.sesion.pelicula_id]),
            {"sesion": self.sesion.id, "butacas": ["1-1", "1-2"]})
        self.client.post(reverse("reservas:confirmacion_compra"))

        self.assertEqual(self.recaudacion(self.corta),
                         self.sala.precio_entrada * 2)


class TestServicioButacas(BaseCine):
    """La capa que decide qué butacas están libres."""

    def peticion(self):
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.test import RequestFactory

        peticion = RequestFactory().get("/")
        SessionMiddleware(lambda r: None).process_request(peticion)
        peticion.session.save()
        return peticion

    def test_etiqueta_legible_de_la_butaca(self):
        self.assertEqual(butacas_svc.etiqueta(1, 7), "A7")
        self.assertEqual(butacas_svc.etiqueta(3, 12), "C12")

    def test_reservar_devuelve_los_conflictos(self):
        primera = self.peticion()
        butacas_svc.reservar(self.sesion, [(1, 1)], primera)

        segunda = self.peticion()
        conflictos = butacas_svc.reservar(self.sesion, [(1, 1), (1, 2)], segunda)

        self.assertEqual(conflictos, ["A1"])
        self.assertEqual(
            ReservaButaca.objects.filter(session_key=segunda.session.session_key)
                                 .count(), 1,
            "la que sí estaba libre se reserva igual")

    def test_volver_a_elegir_sustituye_la_seleccion_anterior(self):
        peticion = self.peticion()
        butacas_svc.reservar(self.sesion, [(1, 1), (1, 2)], peticion)
        butacas_svc.reservar(self.sesion, [(5, 5)], peticion)

        reservadas = {(r.fila, r.numero) for r in
                      ReservaButaca.objects.filter(sesion=self.sesion)}
        self.assertEqual(reservadas, {(5, 5)})
