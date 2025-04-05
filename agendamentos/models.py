from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.timezone import make_aware, localtime
from django.conf import settings


class Barbeiro(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    foto = models.ImageField(upload_to='barbeiros/', blank=True, null=True)

    def __str__(self):
        return self.nome


class HorarioBloqueado(models.Model):
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE)
    data_horario = models.DateTimeField()
    motivo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('barbeiro', 'data_horario')

    def __str__(self):
        data_horario_com_tz = make_aware(self.data_horario) if self.data_horario.tzinfo is None else self.data_horario
        return f"{self.barbeiro.nome} - {localtime(data_horario_com_tz).strftime('%d/%m/%Y %H:%M')}"


class Agendamento(models.Model):
    nome_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField(null=True, blank=True)
    data_horario_reserva = models.DateTimeField()
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.SET_NULL, null=True, blank=True)

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('recusado', 'Recusado'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')

    disponivel = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['data_horario_reserva', 'barbeiro'], name='unique_agendamento_por_barbeiro')
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def processar_status(self):
        if self.status == "recusado":
            self.delete()
        elif self.status == "aceito":
            self.enviar_email()

    def enviar_email(self):
        if self.email_cliente:
            nome_negocio = getattr(settings, "NOME_NEGOCIO", 'Sua Barbearia')
            email_remetente = getattr(settings, "EMAIL_REMETENTE", '')
            nome_barbeiro = self.barbeiro.nome if self.barbeiro else "nosso barbeiro"

            if self.status == "aceito":
                assunto = f"✅ Agendamento Confirmado - {nome_negocio}"
                mensagem = (
                    f"Olá {self.nome_cliente},\n\n"
                    f"Seu agendamento com *{nome_barbeiro}* foi CONFIRMADO!\n\n"
                    f"📅 Data e Hora: {self.data_horario_reserva.strftime('%d/%m/%Y %H:%M')}\n"
                    f"📍 Local: {nome_negocio}\n\n"
                    "Estamos ansiosos para te receber!\n\n"
                    f"Abraços,\n{nome_negocio}"
                )
            else:
                assunto = f"❌ Agendamento Recusado - {nome_negocio}"
                mensagem = (
                    f"Olá {self.nome_cliente},\n\n"
                    f"Infelizmente, seu agendamento com *{nome_barbeiro}* não pôde ser confirmado "
                    f"para o dia *{self.data_horario_reserva.strftime('%d/%m/%Y %H:%M')}*.\n\n"
                    "Você pode tentar novamente escolhendo outro horário disponível no site.\n\n"
                    f"Atenciosamente,\n{nome_negocio}"
                )

            try:
                send_mail(
                    assunto,
                    mensagem,
                    email_remetente,
                    [self.email_cliente],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Erro ao enviar e-mail: {e}")

    def __str__(self):
        if self.data_horario_reserva is not None:
            data_horario_com_tz = make_aware(self.data_horario_reserva) if self.data_horario_reserva.tzinfo is None else self.data_horario_reserva
            status = "Disponível" if self.disponivel else "Fechado"
            barbeiro_str = f" [{self.barbeiro.nome}]" if self.barbeiro else ""
            return f"{self.nome_cliente} - {localtime(data_horario_com_tz).strftime('%d/%m/%Y %H:%M')} ({status}){barbeiro_str}"
        return f"{self.nome_cliente} - (Sem data)"
