from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def is_cliente(user):
    return user.is_authenticated and user.groups.filter(name="Cliente").exists()

cliente_required = user_passes_test(is_cliente, login_url='agendamentos:login')
