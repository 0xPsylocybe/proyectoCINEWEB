from django import template

from usuarios.decorators import es_gestor

register = template.Library()


@register.filter
def is_gestor(user):
    """Filtro para plantillas: {% if user|is_gestor %} ... {% endif %}."""
    return es_gestor(user)
