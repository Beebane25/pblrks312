# Generated by Django 5.0.6 on 2024-12-09 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0003_remove_client_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]