# Generated by Django 5.2 on 2025-04-26 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='clientes/'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='nome',
            field=models.CharField(default='Cliente', max_length=100),
        ),
    ]
