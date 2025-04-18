from django.db import models
from django.utils.timezone import make_aware, localtime
from .barbeiro import Barbeiro

class HorarioBloqueado(models.Model):
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE)
    data_horario = models.DateTimeField()
    motivo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('barbeiro', 'data_horario')

    def __str__(self):
        if not self.data_horario:
            return f"{self.barbeiro.nome} - (Sem horário definido)"
        horario = make_aware(self.data_horario) if self.data_horario.tzinfo is None else self.data_horario
        return f"{self.barbeiro.nome} - {localtime(horario).strftime('%d/%m/%Y %H:%M')}"

DIAS_SEMANA = [
    (0, 'Segunda-feira'),
    (1, 'Terça-feira'),
    (2, 'Quarta-feira'),
    (3, 'Quinta-feira'),
    (4, 'Sexta-feira'),
    (5, 'Sábado'),
    (6, 'Domingo'),
]

class BloqueioSemanalPadrao(models.Model):
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE)
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    motivo = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('barbeiro', 'dia_semana', 'hora_inicio', 'hora_fim')
        verbose_name = "Bloqueio Padrão Semanal"
        verbose_name_plural = "Bloqueios Padrão Semanais"

    def __str__(self):
        dia_nome = dict(DIAS_SEMANA).get(self.dia_semana, 'Desconhecido')
        return f"{self.barbeiro.nome} - {dia_nome} ({self.hora_inicio} às {self.hora_fim})"
