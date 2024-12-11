from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from .models import Client

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            client = Client.objects.get(username=username)
            if check_password(password, client.password):
                return client
        except Client.DoesNotExist:
            return None