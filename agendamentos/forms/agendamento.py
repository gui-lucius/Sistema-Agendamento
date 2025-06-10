from django import forms
from django.core.exceptions import ValidationError
from agendamentos.core.models import Agendamento

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = '__all__'
        widgets = {
            'motivo_cancelamento': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Descreva o motivo do cancelamento'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        motivo = cleaned_data.get('motivo_cancelamento')

        if status == 'recusado' and not motivo:
            raise ValidationError({'motivo_cancelamento': "Informe o motivo do cancelamento."})
        return cleaned_data
