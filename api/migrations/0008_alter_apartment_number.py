# Generated by Django 4.0 on 2021-12-21 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_block_number_alter_floor_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='number',
            field=models.PositiveSmallIntegerField(unique=True, verbose_name='Номер квартиры'),
        ),
    ]
