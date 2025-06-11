from django import forms
from agendamentos.core.models import Barbeiro

class BarbeiroForm(forms.ModelForm):
    class Meta:
        model = Barbeiro
        fields = '__all__'
        widgets = {
            'foto': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'capture': 'user',
            }),
        }
