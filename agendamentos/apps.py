from django.apps import AppConfig
import importlib

class AgendamentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agendamentos'
    verbose_name = 'Gestão de Agendamentos'

    def ready(self):
        importlib.import_module('agendamentos.core.utils.signals')
