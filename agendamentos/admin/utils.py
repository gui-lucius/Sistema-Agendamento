from agendamentos.core.models import Barbeiro

def is_dono(user):
    return user.groups.filter(name='Dono').exists()


class RestrictToOwnDataMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or is_dono(request.user):
            return qs

        # Protege para modelos sem campo "barbeiro"
        if hasattr(self.model, 'barbeiro'):
            return qs.filter(barbeiro__usuario=request.user)

        return qs  # sem filtro se não tiver relação com barbeiro

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or is_dono(request.user):
            return True
        return obj is None or getattr(obj, 'barbeiro', None) and obj.barbeiro.usuario == request.user

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)


def atribuir_barbeiro_automaticamente(request, obj):
    if not (request.user.is_superuser or is_dono(request.user)) and not obj.barbeiro_id:
        try:
            obj.barbeiro = Barbeiro.objects.get(usuario=request.user)
        except Barbeiro.DoesNotExist:
            pass
