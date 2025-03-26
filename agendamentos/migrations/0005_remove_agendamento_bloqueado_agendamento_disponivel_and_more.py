# Generated by Django 5.0.6 on 2025-02-11 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agendamentos', '0004_agendamento_bloqueado_alter_agendamento_nome_cliente'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agendamento',
            name='bloqueado',
        ),
        migrations.AddField(
            model_name='agendamento',
            name='disponivel',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='agendamento',
            name='nome_cliente',
            field=models.CharField(default='Cliente Desconhecido', max_length=100),
            preserve_default=False,
        ),
    ]
