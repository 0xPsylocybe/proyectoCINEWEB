"""Vistas de la compra: carrito con butacas, confirmacion y resguardo."""

from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from cartelera.models import Sesion
from peliculas.models import Peliculas
from restauracion.models import Producto, VentaProducto
from .models import MINUTOS_RESERVA
from . import butacas as butacas_svc
from .models import VentaEntrada
from .forms import CarritoEntradaForm, ProductoCarritoForm


def _butacas_del_post(request):
    """Lee las butacas marcadas en el formulario: llegan como "fila-numero"."""
    seleccionadas = []
    for valor in request.POST.getlist('butacas'):
        try:
            fila, numero = valor.split('-')
            seleccionadas.append((int(fila), int(numero)))
        except (ValueError, TypeError):
            continue
    return seleccionadas


def carrito_compra(request, pelicula_pk=None):
    """Carrito: sesión + butacas + productos de restauración."""

    pelicula = None
    if pelicula_pk:
        pelicula = get_object_or_404(Peliculas, pk=pelicula_pk)

    if request.method == 'POST':
        form_entradas = CarritoEntradaForm(request.POST, pelicula_pk=pelicula_pk)
        form_productos = ProductoCarritoForm(request.POST)

        if form_entradas.is_valid() and form_productos.is_valid():
            sesion = form_entradas.cleaned_data['sesion']
            seleccionadas = _butacas_del_post(request)

            if not seleccionadas:
                messages.error(request, 'Selecciona al menos una butaca.')
                return redirect(_url_carrito(pelicula_pk, sesion.id))

            # Bloquea las butacas durante 30 minutos
            conflictos = butacas_svc.reservar(sesion, seleccionadas, request)
            if conflictos:
                messages.error(
                    request,
                    'Alguien se adelantó con %s. Elige otras butacas.' % ', '.join(conflictos)
                )
                return redirect(_url_carrito(pelicula_pk, sesion.id))

            request.session['carrito_sesion_id'] = sesion.id
            request.session['carrito_productos'] = {}

            for item in form_productos.get_productos_seleccionados():
                request.session['carrito_productos'][str(item['producto'].id)] = {
                    'id': item['producto'].id,
                    'nombre': item['producto'].nombre,
                    'precio': str(item['producto'].precio),
                    'cantidad': item['cantidad'],
                    'total': str(item['total'])
                }

            request.session.modified = True
            return redirect('reservas:confirmacion_compra')

        sesion_preseleccionada = form_entradas.cleaned_data.get('sesion')
    else:
        # Sesión preseleccionada desde el botón "Comprar" de la cartelera
        sesion_id = request.GET.get('sesion')
        sesion_preseleccionada = Sesion.objects.filter(pk=sesion_id).first() if sesion_id else None

        initial = {'sesion': sesion_preseleccionada} if sesion_preseleccionada else None
        form_entradas = CarritoEntradaForm(initial=initial, pelicula_pk=pelicula_pk)
        form_productos = ProductoCarritoForm()

    contexto = {
        'pelicula': pelicula,
        'sesion_preseleccionada': sesion_preseleccionada,
        'mapa_butacas': butacas_svc.mapa(sesion_preseleccionada, request) if sesion_preseleccionada else None,
        'minutos_reserva': MINUTOS_RESERVA,
        'form_entradas': form_entradas,
        'form_productos': form_productos,
    }

    return render(request, 'reservas/carrito_compra.html', contexto)


def _url_carrito(pelicula_pk, sesion_id):
    """Vuelve al carrito conservando película y sesión."""
    if pelicula_pk:
        base = reverse('reservas:carrito_pelicula', args=[pelicula_pk])
    else:
        base = reverse('reservas:carrito')
    return f'{base}?sesion={sesion_id}'


def confirmacion_compra(request):
    """Vista de confirmación de compra antes de guardar."""

    # Obtener datos de la sesión
    sesion_id = request.session.get('carrito_sesion_id')
    productos_data = request.session.get('carrito_productos', {})

    if not sesion_id:
        messages.error(request, 'Carrito vacío o expirado')
        return redirect('reservas:carrito')

    sesion = get_object_or_404(Sesion, id=sesion_id)

    # Las butacas siguen bloqueadas solo si la reserva no ha caducado
    reservas = butacas_svc.mis_reservas(sesion, request)
    if not reservas:
        messages.error(
            request,
            'Tu reserva de butacas ha caducado (%d minutos). Vuelve a elegirlas.' % MINUTOS_RESERVA
        )
        return redirect(_url_carrito(None, sesion.id))

    cantidad_entradas = len(reservas)
    precio_entrada = sesion.sala.precio_entrada
    total_entradas = precio_entrada * cantidad_entradas
    expira_en = min(r.expira_en for r in reservas)

    # Reconstruir productos desde datos de sesión
    productos_carrito = []
    total_productos = Decimal('0.00')
    for producto_id, datos in productos_data.items():
        total_linea = Decimal(datos['total'])
        productos_carrito.append({
            'nombre': datos['nombre'],
            'cantidad': datos['cantidad'],
            'precio': Decimal(datos['precio']),
            'total': total_linea
        })
        total_productos += total_linea

    total_compra = total_entradas + total_productos

    if request.method == 'POST':
        # AQUÍ se guarda la compra
        venta_entrada = VentaEntrada.objects.create(
            sesion=sesion,
            cantidad=cantidad_entradas,
            precio_unitario=precio_entrada,
            total_venta=total_entradas
        )

        # Los bloqueos pasan a ser butacas vendidas
        perdidas = butacas_svc.confirmar(venta_entrada, sesion, request)
        if perdidas:
            venta_entrada.delete()
            request.session.pop('carrito_sesion_id', None)
            messages.error(
                request,
                'Se vendieron %s mientras confirmabas. Vuelve a elegir butacas.' % ', '.join(perdidas)
            )
            return redirect(_url_carrito(None, sesion.id))

        ventas_productos = []
        for producto_id, datos in productos_data.items():
            producto = get_object_or_404(Producto, id=producto_id)
            ventas_productos.append(VentaProducto.objects.create(
                producto=producto,
                cantidad=datos['cantidad'],
                total_venta=Decimal(datos['total'])
            ))

        # Limpiar el carrito y dejar el resguardo para la pantalla final
        request.session.pop('carrito_sesion_id', None)
        request.session.pop('carrito_productos', None)
        request.session['ultima_compra'] = {
            'venta_id': venta_entrada.id,
            'productos_ids': [v.id for v in ventas_productos],
            'total': str(total_compra),
        }

        return redirect('reservas:compra_exitosa')

    contexto = {
        'sesion': sesion,
        'cantidad_entradas': cantidad_entradas,
        'butacas': reservas,
        'expira_en': expira_en,
        'precio_entrada': precio_entrada,
        'total_entradas': total_entradas,
        'productos_carrito': productos_carrito,
        'total_productos': total_productos,
        'total_compra': total_compra,
    }

    return render(request, 'reservas/confirmacion_compra.html', contexto)


def compra_exitosa(request):
    """Resguardo de la compra: qué se ha comprado y con qué localizador.

    Los datos se recuperan de lo que dejó `confirmacion_compra` en la sesión.
    Se conservan ahí para que recargar la página siga mostrando el resguardo.
    """
    resumen = request.session.get('ultima_compra')
    if not resumen:
        messages.info(request, 'No hay ninguna compra reciente que mostrar.')
        return redirect('cartelera')

    venta = (VentaEntrada.objects
             .select_related('sesion__pelicula', 'sesion__sala')
             .prefetch_related('butacas')
             .filter(pk=resumen['venta_id'])
             .first())
    if not venta:
        request.session.pop('ultima_compra', None)
        messages.info(request, 'Esa compra ya no existe.')
        return redirect('cartelera')

    productos = (VentaProducto.objects
                 .select_related('producto')
                 .filter(pk__in=resumen.get('productos_ids', [])))

    contexto = {
        'venta': venta,
        'sesion': venta.sesion,
        'butacas': venta.butacas.all(),
        'productos': productos,
        'total_productos': sum(v.total_venta for v in productos),
        'total': Decimal(resumen['total']),
        # Un localizador con pinta de entrada de cine
        'localizador': 'CL-%06d' % venta.id,
    }
    return render(request, 'reservas/compra_exitosa.html', contexto)
