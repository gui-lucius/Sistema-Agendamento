from django.db import models
from agendamentos.core.models import Barbeiro

class ConversaCliente(models.Model):
    telefone = models.CharField(max_length=20, unique=True)
    estado = models.CharField(max_length=50, default="aguardando_inicio")
    barbeiro = models.ForeignKey(Barbeiro, null=True, blank=True, on_delete=models.SET_NULL)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.telefone} - {self.estado}"