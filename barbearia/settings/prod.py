from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "barbearia-rd.com.br",
    "www.barbearia-rd.com.br",
    "barbearia-rd-a3b518df45e1.herokuapp.com"
]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
