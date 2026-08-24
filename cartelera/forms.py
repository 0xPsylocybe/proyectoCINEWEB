from django import forms
from django.core.exceptions import ValidationError
from .models import Sesion, Sala
from peliculas.models import Peliculas


class SesionForm(forms.ModelForm):
    class Meta:
        model = Sesion
        fields = ['pelicula', 'sala', 'horario']
        widgets = {
            'pelicula': forms.Select(attrs={'class': 'form-control'}),
            'sala': forms.Select(attrs={'class': 'form-control'}),
            'horario': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        sala = cleaned_data.get('sala')
        horario = cleaned_data.get('horario')

        if sala and horario:
            # Validar solapamientos
            sesion = Sesion(pelicula=cleaned_data.get('pelicula'), sala=sala, horario=horario)
            if self.instance.pk:
                sesion.pk = self.instance.pk
            try:
                sesion.clean()
            except ValidationError as e:
                raise ValidationError(e.message)

        return cleaned_data


class RellenarSesionesForm(forms.Form):
    peliculas = forms.ModelMultipleChoiceField(
        queryset=Peliculas.objects.filter(detalles__en_cartelera=True),
        widget=forms.CheckboxSelectMultiple,
        label='Selecciona películas',
        required=True
    )

    salas = forms.ModelMultipleChoiceField(
        queryset=Sala.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Selecciona salas',
        required=True
    )

    fecha_inicio = forms.DateField(
        label='Fecha inicio',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )

    fecha_fin = forms.DateField(
        label='Fecha fin',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )

    borrar_existentes = forms.BooleanField(
        label='Borrar sesiones existentes de estas películas',
        required=False,
        initial=False
    )
