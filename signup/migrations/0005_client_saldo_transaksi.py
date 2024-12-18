# Generated by Django 5.0.6 on 2024-12-13 05:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_alter_postmenu_gambar'),
        ('signup', '0004_client_last_login'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='saldo',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
        migrations.CreateModel(
            name='Transaksi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jenis', models.CharField(choices=[('topup', 'Top-Up'), ('pembelian', 'Pembelian')], max_length=10)),
                ('nominal', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('waktu_transaksi', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signup.client')),
                ('menu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.postmenu')),
            ],
        ),
    ]