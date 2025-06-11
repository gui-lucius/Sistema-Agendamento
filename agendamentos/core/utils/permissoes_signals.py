from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission

@receiver(post_migrate)
def criar_grupos_padrao(sender, **kwargs):
    cliente_group, _ = Group.objects.get_or_create(name='Cliente')

    colaborador_group, _ = Group.objects.get_or_create(name='Colaborador')
    permissoes_colaborador = [
        'add_agendamento',
        'change_agendamento',
        'view_agendamento',
    ]
    atribuir_permissoes(colaborador_group, permissoes_colaborador)

    dono_group, _ = Group.objects.get_or_create(name='Dono')
    permissoes_dono = [
        'add_agendamento',
        'change_agendamento',
        'delete_agendamento',
        'view_agendamento',
        'add_barbeiro',
        'change_barbeiro',
        'delete_barbeiro',
        'view_barbeiro',
    ]
    atribuir_permissoes(dono_group, permissoes_dono)

    print("🔐 Grupos e permissões criados/atualizados com sucesso!")

def atribuir_permissoes(grupo, codigos_permissoes):
    for codename in codigos_permissoes:
        try:
            perm = Permission.objects.get(codename=codename)
            grupo.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"[!] Permissão '{codename}' não encontrada.")
