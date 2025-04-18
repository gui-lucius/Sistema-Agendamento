from django.db import models
from django.contrib.auth.models import User

class Barbeiro(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    foto = models.ImageField(upload_to='barbeiros/', blank=True, null=True)

    def __str__(self):
        return self.nome
