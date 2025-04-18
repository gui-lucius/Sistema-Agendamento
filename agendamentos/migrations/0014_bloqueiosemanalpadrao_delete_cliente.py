# Generated by Django 5.2 on 2025-04-11 21:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agendamentos', '0013_cliente'),
    ]

    operations = [
        migrations.CreateModel(
            name='BloqueioSemanalPadrao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.IntegerField(choices=[(0, 'Segunda-feira'), (1, 'Terça-feira'), (2, 'Quarta-feira'), (3, 'Quinta-feira'), (4, 'Sexta-feira'), (5, 'Sábado'), (6, 'Domingo')])),
                ('hora_inicio', models.TimeField()),
                ('hora_fim', models.TimeField()),
                ('motivo', models.CharField(blank=True, max_length=255)),
                ('barbeiro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agendamentos.barbeiro')),
            ],
            options={
                'verbose_name': 'Bloqueio Padrão Semanal',
                'verbose_name_plural': 'Bloqueios Padrão Semanais',
                'unique_together': {('barbeiro', 'dia_semana', 'hora_inicio', 'hora_fim')},
            },
        ),
        migrations.DeleteModel(
            name='Cliente',
        ),
    ]
