from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "barbearia-rd.com.br",
    "www.barbearia-rd.com.br",
    "barbearia-rd-a3b518df45e1.herokuapp.com",
    "c6a7-2804-ef4-5795-9f00-7033-2dcd-87d9-25bd.ngrok-free.app"
]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
