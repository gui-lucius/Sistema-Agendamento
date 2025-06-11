from .agendamento import *
from .barbeiro import *
from .barbearia import *
from .bloqueios import *
from .user import *

# Oculta o Group do admin
from django.contrib.auth.models import Group
from django.contrib import admin

admin.site.unregister(Group)
