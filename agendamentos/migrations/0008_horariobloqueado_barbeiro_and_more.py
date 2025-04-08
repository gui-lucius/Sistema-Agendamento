# Generated by Django 5.1.5 on 2025-04-05 03:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agendamentos', '0007_barbeiro_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='horariobloqueado',
            name='barbeiro',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='agendamentos.barbeiro'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='horariobloqueado',
            name='data_horario',
            field=models.DateTimeField(),
        ),
        migrations.AlterUniqueTogether(
            name='horariobloqueado',
            unique_together={('barbeiro', 'data_horario')},
        ),
    ]
