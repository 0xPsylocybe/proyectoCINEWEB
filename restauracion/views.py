from django.shortcuts import render
from .models import Producto, Categoria


def catalogo_restauracion(request):
    """Catálogo de productos de restauración."""
    productos = Producto.objects.select_related('categoria').all()
    categorias = Categoria.objects.all()

    contexto = {
        'productos': productos,
        'categorias': categorias,
    }

    return render(request, 'restauracion/catalogo.html', contexto)
