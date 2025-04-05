from django.contrib import admin
from .models import Agendamento, HorarioBloqueado, Barbeiro


@admin.register(HorarioBloqueado)
class HorarioBloqueadoAdmin(admin.ModelAdmin):
    list_display = ('data_horario', 'motivo', 'barbeiro')
    search_fields = ('data_horario', 'motivo', 'barbeiro__nome')
    list_filter = ('barbeiro',)
    ordering = ('-data_horario',)
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(barbeiro__usuario=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.barbeiro.usuario != request.user:
            return False
        return True


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('nome_cliente', 'data_horario_reserva', 'status', 'barbeiro', 'disponivel')
    list_display_links = ('nome_cliente', 'data_horario_reserva')
    list_filter = ('status', 'data_horario_reserva', 'barbeiro')
    search_fields = ('nome_cliente', 'email_cliente')
    date_hierarchy = 'data_horario_reserva'
    ordering = ('-data_horario_reserva',)
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(barbeiro__usuario=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.barbeiro.usuario != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.barbeiro_id:
            try:
                obj.barbeiro = Barbeiro.objects.get(usuario=request.user)
            except Barbeiro.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
        obj.processar_status()


@admin.register(Barbeiro)
class BarbeiroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'usuario')
    search_fields = ('nome', 'email')
