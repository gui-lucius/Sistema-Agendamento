from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import localtime, make_aware
from django.conf import settings
from django.core.mail import send_mail
from uuid import uuid4
from .barbeiro import Barbeiro

class Agendamento(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nome_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField(null=True, blank=True)
    data_horario_reserva = models.DateTimeField()
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.SET_NULL, null=True, blank=True)
    servico = models.CharField(max_length=100, blank=True, null=True)
    lembrete_minutos = models.PositiveIntegerField(default=60)

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('recusado', 'Recusado'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    motivo_cancelamento = models.TextField("Motivo do cancelamento", blank=True, null=True)
    disponivel = models.BooleanField(default=True)
    lembrete_enviado = models.BooleanField(default=False)
    cancel_token = models.UUIDField(default=uuid4, unique=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['data_horario_reserva', 'barbeiro'], name='unique_agendamento_por_barbeiro')
        ]

    def save(self, *args, **kwargs):
        status_original = None
        if self.pk:
            status_original = Agendamento.objects.get(pk=self.pk).status
        super().save(*args, **kwargs)
        if self.status != status_original:
            self.enviar_email()

    def enviar_email(self):
        if not self.email_cliente:
            return

        nome_negocio = getattr(settings, "NOME_NEGOCIO", "Sua Barbearia")
        remetente = getattr(settings, "EMAIL_REMETENTE", "")
        horario_str = localtime(self.data_horario_reserva).strftime('%d/%m/%Y %H:%M')
        nome_barbeiro = self.barbeiro.nome if self.barbeiro else "nosso barbeiro"
        servico_str = self.servico or "Serviço não informado"
        link_cancelamento = f"{settings.DOMINIO_SITE}/cancelar-agendamento/{self.pk}/{self.cancel_token}/"

        if self.status == "aceito":
            assunto = f"✅ Agendamento Confirmado - {nome_negocio}"
            mensagem = (
                f"Olá {self.nome_cliente},\n\n"
                f"Seu agendamento foi confirmado com sucesso!\n\n"
                f"📅 Data e Hora: {horario_str}\n"
                f"💈 Barbeiro: {nome_barbeiro}\n"
                f"🔧 Serviço: {servico_str}\n"
                f"⏰ Lembrete: {self.lembrete_minutos} minutos antes\n\n"
                f"Se não puder comparecer, cancele por aqui:\n{link_cancelamento}\n\n"
                f"Abraços,\nEquipe {nome_negocio}"
            )
        elif self.status == "recusado":
            assunto = f"❌ Agendamento Recusado - {nome_negocio}"
            motivo = self.motivo_cancelamento or "O barbeiro não informou o motivo."
            link_remarcacao = f"{settings.DOMINIO_SITE}/barbeiro/{self.barbeiro.pk}/calendario" if self.barbeiro else settings.DOMINIO_SITE

            mensagem = (
                f"Olá {self.nome_cliente},\n\n"
                f"Seu agendamento com {nome_barbeiro} foi RECUSADO.\n\n"
                f"📅 Data e Hora: {horario_str}\n"
                f"🔧 Serviço: {servico_str}\n\n"
                f"📌 Motivo do cancelamento: {motivo}\n\n"
                f"👉 Clique aqui para reagendar: {link_remarcacao}\n\n"
                f"Equipe {nome_negocio}"
            )
        else:
            return

        try:
            send_mail(assunto, mensagem, remetente, [self.email_cliente], fail_silently=True)
        except Exception as e:
            print(f"[ERRO EMAIL] Falha ao enviar para cliente: {e}")

    def processar_status(self):
        if self.status == "recusado":
            self.delete()

    def __str__(self):
        if self.data_horario_reserva:
            horario = make_aware(self.data_horario_reserva) if self.data_horario_reserva.tzinfo is None else self.data_horario_reserva
            status_str = "Disponível" if self.disponivel else "Fechado"
            barbeiro_info = f" [{self.barbeiro.nome}]" if self.barbeiro else ""
            return f"{self.nome_cliente} - {localtime(horario).strftime('%d/%m/%Y %H:%M')} ({status_str}){barbeiro_info}"
        return f"{self.nome_cliente} - (Sem data)"
