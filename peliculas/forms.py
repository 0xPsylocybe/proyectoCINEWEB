from django import forms
from .models import Peliculas,Director,Genero

class PeliculasForm(forms.ModelForm):
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
    class Meta:
        model = Director
        fields = ['nombre',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'})
        }
        
class GeneroForm(forms.ModelForm):
    class Meta:
        model = Genero
        fields = ['nombre',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'})
        }