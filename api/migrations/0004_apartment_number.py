# Generated by Django 3.2.9 on 2021-12-08 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20211208_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='apartment',
            name='number',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Номер квартиры'),
            preserve_default=False,
        ),
    ]
