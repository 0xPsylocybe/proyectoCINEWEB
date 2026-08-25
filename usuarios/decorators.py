"""Decoradores de permisos para proteger las vistas de gestion."""

from django.contrib.auth.decorators import user_passes_test


def es_gestor(user):
    """Un gestor es un superusuario o un miembro del grupo 'Gestores'."""
    return user.is_superuser or user.groups.filter(name="Gestores").exists()


# Decorador para proteger las vistas de gestión: si el usuario no es gestor,
# se le redirige a la página de inicio.
gestor_required = user_passes_test(es_gestor, login_url="inicio")
