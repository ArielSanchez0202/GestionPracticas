# Generated by Django 5.1.1 on 2024-11-01 17:53

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinador', '0009_alter_coordinador_rut'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coordinador',
            name='usuario',
        ),
        migrations.AddField(
            model_name='coordinador',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]