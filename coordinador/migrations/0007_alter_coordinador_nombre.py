# Generated by Django 5.1.1 on 2024-10-31 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinador', '0006_alter_coordinador_rut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coordinador',
            name='nombre',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
