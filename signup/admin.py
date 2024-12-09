from django.contrib import admin
from .models import Client, LoginHistory

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('username', 'email','last_login', 'created_at')  # Gunakan atribut yang valid
    search_fields = ('username', 'email')  # Tambahkan pencarian berdasarkan username/email

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('client', 'login_time', 'ip_address', 'status')
    search_fields = ('client__username', 'ip_address', 'status')
    list_filter = ('status', 'login_time')
