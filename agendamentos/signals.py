from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Agendamento
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=Agendamento)
def enviar_email_cliente(sender, instance, created, **kwargs):
    if created:
        return  # só queremos agir em alterações, não na criação

    if not instance.email_cliente:
        return

    try:
        if instance.status == "aceito":
            assunto = f"✅ Agendamento Confirmado - {settings.NOME_NEGOCIO}"
            mensagem = (
                f"Olá {instance.nome_cliente},\n\n"
                f"Seu agendamento foi CONFIRMADO para {instance.data_horario_reserva.strftime('%d/%m/%Y %H:%M')}.\n\n"
                "Obrigado por escolher a gente! 😊"
            )
        elif instance.status == "recusado":
            assunto = f"❌ Agendamento Recusado - {settings.NOME_NEGOCIO}"
            mensagem = (
                f"Olá {instance.nome_cliente},\n\n"
                f"Infelizmente seu agendamento foi recusado para {instance.data_horario_reserva.strftime('%d/%m/%Y %H:%M')}.\n\n"
                "Sinta-se à vontade para escolher outro horário!"
            )
        else:
            return  # status não é relevante

        send_mail(
            assunto,
            mensagem,
            settings.EMAIL_REMETENTE,
            [instance.email_cliente],
            fail_silently=False
        )
        print(f"📧 E-mail enviado para {instance.email_cliente}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar e-mail para o cliente: {e}")
