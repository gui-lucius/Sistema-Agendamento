# Generated by Django 5.1.5 on 2025-04-07 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agendamentos', '0011_alter_agendamento_cancel_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendamento',
            name='lembrete_minutos',
            field=models.PositiveIntegerField(default=60),
        ),
        migrations.AddField(
            model_name='agendamento',
            name='servico',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
