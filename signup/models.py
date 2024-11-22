from django.db import models
from django.utils.timezone import now

class Client(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Untuk menyimpan hash password
    full_name = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.email:
            raise ValueError("Email must be provided")
        super().save(*args, **kwargs)

class LoginHistory(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='login_histories')
    login_time = models.DateTimeField(default=now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('SUCCESS', 'Success'), ('FAIL', 'Fail')])

    def __str__(self):
        return f"{self.client.username} - {self.status} at {self.login_time}"