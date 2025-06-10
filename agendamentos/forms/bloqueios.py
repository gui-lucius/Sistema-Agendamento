from django import forms
from django.forms.widgets import DateInput
from agendamentos.core.models import HorarioBloqueado

class HorarioBloqueadoForm(forms.ModelForm):
    data = forms.DateField(
        label="Data",
        required=True,
        widget=DateInput(attrs={'type': 'date'})
    )
    bloquear_dia_todo = forms.BooleanField(required=False, label="Bloquear o dia todo")
    hora_inicial = forms.TimeField(required=False, label='Hora Inicial')
    hora_final = forms.TimeField(required=False, label='Hora Final')

    class Meta:
        model = HorarioBloqueado
        fields = ['barbeiro', 'motivo']

    def clean(self):
        cleaned_data = super().clean()
        bloquear_dia_todo = cleaned_data.get('bloquear_dia_todo')
        hora_inicial = cleaned_data.get('hora_inicial')
        hora_final = cleaned_data.get('hora_final')

        if not bloquear_dia_todo:
            if not hora_inicial or not hora_final:
                raise forms.ValidationError("Informe hora inicial e final ou marque 'Bloquear o dia todo'.")
            if hora_inicial > hora_final:
                raise forms.ValidationError("A hora final deve ser maior ou igual à inicial.")
        return cleaned_data
