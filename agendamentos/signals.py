from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group
import os

from .models import Barbeiro

@receiver(post_save, sender=Barbeiro)
def adicionar_ao_grupo_colaborador(sender, instance, created, **kwargs):
    if created:
        try:
            grupo = Group.objects.get(name='Colaborador')
            instance.usuario.groups.add(grupo)
            print(f"✅ Usuário {instance.usuario.username} adicionado ao grupo 'Colaborador'")
        except Group.DoesNotExist:
            print("⚠️ Grupo 'Colaborador' não existe. Crie ele no painel admin.")

@receiver(post_delete, sender=Barbeiro)
def deletar_foto_barbeiro(sender, instance, **kwargs):
    if instance.foto and instance.foto.path:
        try:
            if os.path.isfile(instance.foto.path):
                os.remove(instance.foto.path)
                print(f"🧼 Foto removida: {instance.foto.path}")
        except Exception as e:
            print(f"[ERRO] Falha ao excluir imagem do barbeiro: {e}")
