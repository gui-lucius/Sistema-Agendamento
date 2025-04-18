from .agendamento_admin import *
from .barbeiro_admin import *
from .horario_bloqueado_admin import *
from .bloqueio_padrao_admin import *
from .user_admin import *

# Oculta o Group do admin 
from django.contrib.auth.models import Group
from django.contrib import admin
admin.site.unregister(Group)
