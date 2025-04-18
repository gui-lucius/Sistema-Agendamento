from django.core.management.base import BaseCommand
from agendamentos.core.services.lembretes import enviar_lembretes_agendamentos

class Command(BaseCommand):
    help = 'Envia lembretes para clientes antes do horário agendado.'

    def handle(self, *args, **kwargs):
        total = enviar_lembretes_agendamentos()
        self.stdout.write(self.style.SUCCESS(f"✅ Lembretes enviados: {total}"))
