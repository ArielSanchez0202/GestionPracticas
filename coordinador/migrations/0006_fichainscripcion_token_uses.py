# Generated by Django 5.0.6 on 2024-12-01 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinador', '0005_fichainscripcion_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichainscripcion',
            name='token_uses',
            field=models.IntegerField(default=2),
        ),
    ]
