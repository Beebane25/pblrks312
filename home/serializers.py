from rest_framework import serializers
from .models import PostMenu
from signup.models import Client, Transaksi

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'username', 'email', 'saldo']

class TransaksiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaksi
        fields = '__all__'

class PostMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMenu
        fields = ['id', 'nama_menu', 'kategori', 'harga', 'gambar', 'kepuasan']
