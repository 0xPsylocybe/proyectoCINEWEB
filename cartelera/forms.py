from django import forms
from django.core.exceptions import ValidationError
from .models import Sesion


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
