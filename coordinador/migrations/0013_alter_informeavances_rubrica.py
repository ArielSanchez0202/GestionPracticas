# Generated by Django 5.0.6 on 2024-11-26 04:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinador', '0012_alter_informeavances_nota_avance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informeavances',
            name='rubrica',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coordinador.rubrica'),
        ),
    ]
