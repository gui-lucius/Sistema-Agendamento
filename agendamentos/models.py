from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import make_aware, localtime
from django.conf import settings
from uuid import uuid4
from django.core.mail import send_mail


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
        if not self.data_horario:
            return f"{self.barbeiro.nome} - (Sem horário definido)"
        
        data_horario_com_tz = make_aware(self.data_horario) if self.data_horario.tzinfo is None else self.data_horario
        return f"{self.barbeiro.nome} - {localtime(data_horario_com_tz).strftime('%d/%m/%Y %H:%M')}"


class Agendamento(models.Model):
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
        nome_barbeiro = self.barbeiro.nome if self.barbeiro else "nosso barbeiro"
        horario_str = localtime(self.data_horario_reserva).strftime('%d/%m/%Y %H:%M')
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
            mensagem = (
                f"Olá {self.nome_cliente},\n\n"
                f"Seu agendamento com {nome_barbeiro} foi RECUSADO.\n\n"
                f"📅 Data e Hora: {horario_str}\n"
                f"🔧 Serviço: {servico_str}\n\n"
                "O horário pode ter sido preenchido ou o barbeiro ficou indisponível.\n"
                "Você pode voltar e tentar outro horário pelo site.\n\n"
                f"Equipe {nome_negocio}"
            )
        else:
            return

        try:
            send_mail(
                assunto,
                mensagem,
                remetente,
                [self.email_cliente],
                fail_silently=True
            )
        except Exception as e:
            print(f"[ERRO EMAIL] Falha ao enviar para cliente: {e}")

    def processar_status(self):
        if self.status == "recusado":
            self.delete()

    def __str__(self):
        if self.data_horario_reserva:
            data_horario_com_tz = make_aware(self.data_horario_reserva) if self.data_horario_reserva.tzinfo is None else self.data_horario_reserva
            status = "Disponível" if self.disponivel else "Fechado"
            barbeiro_str = f" [{self.barbeiro.nome}]" if self.barbeiro else ""
            return f"{self.nome_cliente} - {localtime(data_horario_com_tz).strftime('%d/%m/%Y %H:%M')} ({status}){barbeiro_str}"
        return f"{self.nome_cliente} - (Sem data)"
