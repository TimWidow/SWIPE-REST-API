# Generated by Django 3.2.9 on 2021-12-08 11:44

import api.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', api.models.UserManager()),
            ],
        ),
    ]
