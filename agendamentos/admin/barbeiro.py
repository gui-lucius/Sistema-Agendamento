from django.contrib import admin
from django.contrib.auth.models import User
from agendamentos.core.models import Barbeiro
from agendamentos.forms.barbeiro import BarbeiroForm
from agendamentos.admin.mixins import RestrictToOwnDataMixin

@admin.register(Barbeiro)
class BarbeiroAdmin(RestrictToOwnDataMixin, admin.ModelAdmin):
    form = BarbeiroForm
    list_display = ('nome', 'email', 'usuario')
    search_fields = ('nome', 'email')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "usuario":
            kwargs["queryset"] = User.objects.filter(groups__name__in=["Dono", "Colaborador"])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
