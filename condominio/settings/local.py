
from .base import *

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

POSTGRES_HOST='localhost'
