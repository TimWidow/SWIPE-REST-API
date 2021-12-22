# Generated by Django 4.0 on 2021-12-21 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_apartment_heating_alter_house_house_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='number',
            field=models.PositiveSmallIntegerField(unique=True, verbose_name='Корпус'),
        ),
        migrations.AlterField(
            model_name='floor',
            name='number',
            field=models.PositiveSmallIntegerField(unique=True, verbose_name='Этаж'),
        ),
        migrations.AlterField(
            model_name='section',
            name='number',
            field=models.PositiveSmallIntegerField(unique=True, verbose_name='Секция'),
        ),
    ]