"""Formularios para dar de alta peliculas, directores y generos."""

from django import forms
from .models import Peliculas,Director,Genero

class PeliculasForm(forms.ModelForm):
    """Formulario para el alta y modificación de películas y subida de pósters."""
    class Meta:
        model = Peliculas
        fields = [
            "titulo",
            "duracion",
            "director",
            "genero",
            "sinopsis",
            "anio",
            "imagen",  
        ]

class DirectorForm(forms.ModelForm):
    """Formulario para la creación rápida de nuevos directores."""
    class Meta:
        model = Director
        fields = ['nombre',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'})
        }
        
class GeneroForm(forms.ModelForm):
    """Formulario para la creación rápida de nuevos géneros cinematográficos."""
    class Meta:
        model = Genero
        fields = ['nombre',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'})
        }