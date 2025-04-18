from agendamentos.core.models import Barbeiro

# ✅ Verifica se o usuário é dono
def is_dono(user):
    return user.groups.filter(name='Dono').exists()


# ✅ Mixin que restringe visualização e edição apenas aos próprios dados
class RestrictToOwnDataMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or is_dono(request.user):
            return qs
        # 🔧 Corrigido aqui — filtra por barbeiro vinculado ao usuário
        return qs.filter(barbeiro__usuario=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or is_dono(request.user):
            return True
        # 🔐 Garante que só o dono do objeto pode editar
        return obj is None or getattr(obj, 'barbeiro', None) and obj.barbeiro.usuario == request.user

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)


# ✅ Preenche automaticamente o barbeiro vinculado ao usuário
def atribuir_barbeiro_automaticamente(request, obj):
    if not (request.user.is_superuser or is_dono(request.user)) and not obj.barbeiro_id:
        try:
            obj.barbeiro = Barbeiro.objects.get(usuario=request.user)
        except Barbeiro.DoesNotExist:
            pass
