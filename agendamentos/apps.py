from django.apps import AppConfig


class AgendamentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agendamentos'
    verbose_name = 'Gestão de Agendamentos'

    def ready(self):
        import agendamentos.signals  
