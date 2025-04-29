from django.contrib import admin
from django import forms
from agendamentos.core.models import Barbeiro
from agendamentos.admin.utils import RestrictToOwnDataMixin
from django.contrib.auth.models import User  # 👈 Importante
# 🚨 Adicionando esse import do User pra poder filtrar depois.

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "usuario":
            kwargs["queryset"] = User.objects.filter(groups__name__in=["Dono", "Colaborador"])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
