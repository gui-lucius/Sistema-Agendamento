from django.apps import AppConfig


class AgendamentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agendamentos'
    verbose_name = 'Gestão de Agendamentos'

    def ready(self):
        from .core.utils import signals  # ou use importlib se quiser mais elegante
