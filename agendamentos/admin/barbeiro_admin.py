from django.contrib import admin
from django import forms
from agendamentos.core.models import Barbeiro
from agendamentos.admin.utils import RestrictToOwnDataMixin

class BarbeiroForm(forms.ModelForm):
    class Meta:
        model = Barbeiro
        fields = '__all__'
        widgets = {
            'foto': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'capture': 'user',
            })
        }

@admin.register(Barbeiro)
class BarbeiroAdmin(RestrictToOwnDataMixin, admin.ModelAdmin):
    form = BarbeiroForm
    list_display = ('nome', 'email', 'usuario')
    search_fields = ('nome', 'email')
