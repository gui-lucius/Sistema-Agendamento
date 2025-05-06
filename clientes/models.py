from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente')
    nome = models.CharField(max_length=100, default="Cliente")  
    telefone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, blank=True, null=True)
    foto = models.ImageField(upload_to='clientes/', blank=True, null=True)
    pontos_fidelidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome or self.user.username
