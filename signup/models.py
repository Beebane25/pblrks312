from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser

class Client(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)  # Tambahkan field last_login


    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.email:
            raise ValueError("Email must be provided")
        super().save(*args, **kwargs)

class Transaksi(models.Model):
    JENIS_TRANSAKSI = (
        ('topup', 'Top-Up'),
        ('pembelian', 'Pembelian'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    jenis = models.CharField(choices=JENIS_TRANSAKSI, max_length=10)
    nominal = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')  # pending, berhasil, gagal
    waktu_transaksi = models.DateTimeField(auto_now_add=True)
    from home.models import PostMenu
    menu = models.ForeignKey(PostMenu, on_delete=models.SET_NULL, null=True, blank=True)  # Untuk pembelian item

class LoginHistory(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='login_histories')
    login_time = models.DateTimeField(default=now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('SUCCESS', 'Success'), ('FAIL', 'Fail')])

    def __str__(self):
        return f"{self.client.username} - {self.status} at {self.login_time}"