from django.contrib import admin
from agendamentos.core.models import BloqueioSemanalPadrao, Barbeiro
from agendamentos.admin.utils import is_dono

@admin.register(BloqueioSemanalPadrao)
class BloqueioSemanalPadraoAdmin(admin.ModelAdmin):
    list_display = ('barbeiro', 'dia_semana', 'hora_inicio', 'hora_fim', 'motivo')
    list_filter = ('barbeiro', 'dia_semana')
    ordering = ('barbeiro', 'dia_semana', 'hora_inicio')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "barbeiro" and not (request.user.is_superuser or is_dono(request.user)):
            try:
                barbeiro = Barbeiro.objects.get(usuario=request.user)
                kwargs["queryset"] = Barbeiro.objects.filter(pk=barbeiro.pk)
                kwargs["initial"] = barbeiro
            except Barbeiro.DoesNotExist:
                kwargs["queryset"] = Barbeiro.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
