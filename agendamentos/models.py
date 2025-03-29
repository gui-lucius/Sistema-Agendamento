from django.db import models
from django.core.mail import send_mail
from django.utils.timezone import make_aware, localtime
from django.core.exceptions import ValidationError
from django.conf import settings  


class HorarioBloqueado(models.Model):
    data_horario = models.DateTimeField(unique=True)
    motivo = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        data_horario_com_tz = make_aware(self.data_horario) if self.data_horario.tzinfo is None else self.data_horario
        return f"Bloqueado: {localtime(data_horario_com_tz).strftime('%d/%m/%Y %H:%M')}"


class Agendamento(models.Model):
    nome_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField(null=True, blank=True)
    data_horario_reserva = models.DateTimeField()

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('recusado', 'Recusado'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')

    disponivel = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['data_horario_reserva'], name='unique_agendamento_horario')
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = Agendamento.objects.get(pk=self.pk).status
            if old_status != self.status:
                if self.status == "recusado":
                    self.delete()
                    return
                self.enviar_email()
        super().save(*args, **kwargs)

    def enviar_email(self):
        if self.email_cliente:
            nome_negocio = getattr(settings, "NOME_NEGOCIO", None)
            email_remetente = getattr(settings, "EMAIL_REMETENTE", None)

            if self.status == "aceito":
                assunto = f"✅ Agendamento Confirmado - {nome_negocio}"
                mensagem = (
                    f"Olá {self.nome_cliente},\n\n"
                    "Seu agendamento foi CONFIRMADO! Estamos ansiosos para recebê-lo.\n\n"
                    f"📅 Data e Hora: {self.data_horario_reserva.strftime('%d/%m/%Y %H:%M')}\n"
                    f"📍 Local: {nome_negocio}\n\n"
                    "Caso precise remarcar, entre em contato conosco.\n\n"
                    f"Atenciosamente,\n{nome_negocio}"
                )
            else:
                assunto = f"❌ Agendamento Recusado - {nome_negocio}"
                mensagem = (
                    f"Olá {self.nome_cliente},\n\n"
                    "Infelizmente, não conseguimos confirmar seu agendamento.\n\n"
                    "Sugerimos que tente outro horário disponível em nosso calendário.\n\n"
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
            return f"{self.nome_cliente} - {localtime(data_horario_com_tz).strftime('%d/%m/%Y %H:%M')} ({status})"
        return f"{self.nome_cliente} - (Sem data)"
