# Generated by Django 3.2.9 on 2021-11-19 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20211120_0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='house_status',
            field=models.CharField(choices=[('ECO', 'Эконом'), ('COMFORT', 'Комфорт'), ('COMFORT', 'Бизнес'), ('ELITE', 'Элитный')], max_length=10),
        ),
        migrations.AlterField(
            model_name='house',
            name='house_type',
            field=models.CharField(choices=[('MULTI', 'Многоквартирный'), ('PRIVATE', 'Частный')], max_length=255),
        ),
    ]