# Generated by Django 5.1.5 on 2025-04-06 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agendamentos', '0008_horariobloqueado_barbeiro_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendamento',
            name='lembrete_enviado',
            field=models.BooleanField(default=False),
        ),
    ]
