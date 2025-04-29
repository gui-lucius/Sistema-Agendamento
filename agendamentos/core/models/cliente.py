import os
import uuid
from django.db import models
from django.contrib.auth.models import User

def caminho_foto_cliente(instance, filename):
    ext = filename.split('.')[-1]
    nome_arquivo = f"{uuid.uuid4()}.{ext}"
    return os.path.join('clientes', nome_arquivo)

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to=caminho_foto_cliente, blank=True, null=True)

    def __str__(self):
        return self.nome
