from django.contrib.auth.models import Group
from django.contrib.auth import logout

class ClienteSessionMiddleware:
    """
    Se o usuário estiver autenticado e **não for Cliente**,
    remove ele da sessão do frontend (mas não interfere no admin).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if not path.startswith('/admin') and not path.startswith('/static'):

            user = getattr(request, 'user', None)

            if user and user.is_authenticated:
                if not user.groups.filter(name="Cliente").exists():
                    logout(request)

        return self.get_response(request)
