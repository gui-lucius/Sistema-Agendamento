from django.contrib import admin
from .models import Agendamento, HorarioBloqueado


@admin.register(HorarioBloqueado)
class HorarioBloqueadoAdmin(admin.ModelAdmin):
    list_display = ('data_horario', 'motivo')
    search_fields = ('data_horario', 'motivo')
    list_per_page = 25
    ordering = ('-data_horario',)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('nome_cliente', 'data_horario_reserva', 'status', 'disponivel')
    list_display_links = ('nome_cliente', 'data_horario_reserva')
    list_filter = ('status', 'data_horario_reserva')
    search_fields = ('nome_cliente', 'email_cliente')
    date_hierarchy = 'data_horario_reserva'
    ordering = ('-data_horario_reserva',)
    list_per_page = 25
