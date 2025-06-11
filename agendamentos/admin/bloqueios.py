from django.contrib import admin
from datetime import datetime, timedelta

from agendamentos.core.models import (
    HorarioBloqueado,
    BloqueioSemanalPadrao,
    Barbeiro
)
from agendamentos.forms.bloqueios import HorarioBloqueadoForm
from agendamentos.admin.mixins import is_dono


@admin.register(HorarioBloqueado)
class HorarioBloqueadoAdmin(admin.ModelAdmin):
    form = HorarioBloqueadoForm
    list_display = ('data_horario', 'motivo', 'barbeiro')
    search_fields = ('data_horario', 'motivo', 'barbeiro__nome')
    list_filter = ('barbeiro',)
    ordering = ('-data_horario',)
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        barbeiro = form.cleaned_data['barbeiro']
        data = form.cleaned_data['data']
        motivo = form.cleaned_data['motivo']
        bloquear_dia_todo = form.cleaned_data.get('bloquear_dia_todo')

        if bloquear_dia_todo:
            hora_inicial = datetime.strptime("09:00", "%H:%M").time()
            hora_final = datetime.strptime("21:00", "%H:%M").time()
        else:
            hora_inicial = form.cleaned_data['hora_inicial']
            hora_final = form.cleaned_data['hora_final']

        atual = datetime.combine(data, hora_inicial)
        fim = datetime.combine(data, hora_final)

        while atual <= fim:
            HorarioBloqueado.objects.get_or_create(
                barbeiro=barbeiro,
                data_horario=atual,
                defaults={'motivo': motivo}
            )
            atual += timedelta(hours=1)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or is_dono(request.user):
            return qs
        return qs.filter(barbeiro__usuario=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or is_dono(request.user):
            return True
        if obj and obj.barbeiro.usuario != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "barbeiro" and not (request.user.is_superuser or is_dono(request.user)):
            try:
                barbeiro = Barbeiro.objects.get(usuario=request.user)
                kwargs["queryset"] = Barbeiro.objects.filter(pk=barbeiro.pk)
                kwargs["initial"] = barbeiro
            except Barbeiro.DoesNotExist:
                kwargs["queryset"] = Barbeiro.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
