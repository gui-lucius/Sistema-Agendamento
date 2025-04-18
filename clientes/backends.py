from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class ClienteBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.groups.filter(name='Cliente').exists():
                return user
        except User.DoesNotExist:
            return None
