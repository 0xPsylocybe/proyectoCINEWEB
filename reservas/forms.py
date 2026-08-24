from django import forms
from django.forms import inlineformset_factory
from cartelera.models import Sesion
from restauracion.models import Producto, VentaProducto
from .models import VentaEntrada


class CarritoEntradaForm(forms.ModelForm):
    """Selección de sesión. Las entradas salen de las butacas elegidas."""

    class Meta:
        model = VentaEntrada
        fields = ['sesion']
        widgets = {
            'sesion': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_sesion',
            }),
        }

    def __init__(self, *args, **kwargs):
        pelicula_pk = kwargs.pop('pelicula_pk', None)
        super().__init__(*args, **kwargs)

        if pelicula_pk:
            self.fields['sesion'].queryset = Sesion.objects.filter(
                pelicula_id=pelicula_pk
            ).select_related('sala', 'pelicula').order_by('horario')
        else:
            self.fields['sesion'].queryset = Sesion.objects.select_related(
                'sala', 'pelicula'
            ).order_by('horario')

        self.fields['sesion'].label_from_instance = lambda obj: (
            f"{obj.horario.strftime('%d/%m/%Y %H:%M')} - "
            f"{obj.sala.identificador} - {obj.sala.tipo} "
            f"(€{obj.sala.precio_entrada})"
        )


class ProductoCarritoForm(forms.Form):
    """Formulario dinámico para agregar productos al carrito."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrupar productos por categoría
        categorias = {}
        for producto in Producto.objects.select_related('categoria').all():
            cat_nombre = producto.categoria.nombre if producto.categoria else "Sin categoría"
            if cat_nombre not in categorias:
                categorias[cat_nombre] = []
            categorias[cat_nombre].append(producto)

        self._categorias = categorias

        # Crear campos para cada producto
        for cat_nombre, productos in categorias.items():
            for producto in productos:
                field_name = f'producto_{producto.id}'
                self.fields[field_name] = forms.IntegerField(
                    label=f"{producto.nombre} (€{producto.precio})",
                    initial=0,
                    min_value=0,
                    max_value=10,
                    required=False,
                    widget=forms.Select(
                        choices=[(i, i) for i in range(11)],
                        attrs={
                            'class': 'form-select form-select-sm w-auto flex-grow-0 producto-cantidad',
                            'data-product-id': producto.id,
                            'data-price': producto.precio
                        }
                    )
                )

    def campos_por_categoria(self):
        """Devuelve [(nombre_categoria, [bound_fields]), ...] para el template."""
        agrupados = []
        for cat_nombre, productos in self._categorias.items():
            campos = [self[f'producto_{p.id}'] for p in productos]
            agrupados.append((cat_nombre, campos))
        return agrupados

    def get_productos_seleccionados(self):
        """Retorna lista de productos con cantidad > 0."""
        productos_seleccionados = []
        for campo, valor in self.cleaned_data.items():
            if campo.startswith('producto_') and valor:
                producto_id = int(campo.split('_')[1])
                try:
                    producto = Producto.objects.get(id=producto_id)
                    productos_seleccionados.append({
                        'producto': producto,
                        'cantidad': valor,
                        'total': producto.precio * valor
                    })
                except Producto.DoesNotExist:
                    pass
        return productos_seleccionados
