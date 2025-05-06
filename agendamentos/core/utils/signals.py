import os
from django.db.models.signals import post_delete, m2m_changed, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from agendamentos.core.models import Barbeiro

def nome_usuario(user):
    return user.get_full_name() or user.username


@receiver(post_delete, sender=Barbeiro)
def deletar_foto_barbeiro(sender, instance, **kwargs):
    if instance.foto and instance.foto.path:
        try:
            if os.path.isfile(instance.foto.path):
                os.remove(instance.foto.path)
                print(f"🧼 Foto do barbeiro removida: {instance.foto.path}")
        except Exception as e:
            print(f"[ERRO] Falha ao excluir imagem do barbeiro: {e}")

@receiver(m2m_changed, sender=User.groups.through)
def criar_ou_remover_barbeiro_ao_mudar_grupo(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        grupos = Group.objects.filter(pk__in=pk_set).values_list('name', flat=True)
        if 'Colaborador' in grupos or 'Dono' in grupos:
            barbeiro, criado = Barbeiro.objects.get_or_create(
                usuario=instance,
                defaults={
                    'nome': nome_usuario(instance),
                    'email': instance.email
                }
            )
            if criado:
                print(f"✂️ Barbeiro criado automaticamente para '{instance.username}'")

    elif action == 'post_remove':
        grupos_atuais = instance.groups.values_list('name', flat=True)
        if 'Colaborador' not in grupos_atuais and 'Dono' not in grupos_atuais:
            if Barbeiro.objects.filter(usuario=instance).exists():
                Barbeiro.objects.filter(usuario=instance).delete()
                print(f"🗑️ Barbeiro removido: '{instance.username}' não está mais em nenhum grupo válido")

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
