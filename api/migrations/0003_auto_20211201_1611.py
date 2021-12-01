# Generated by Django 3.2.9 on 2021-12-01 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20211130_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='city',
            field=models.CharField(default='Kiev', max_length=255, verbose_name='Город'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='house',
            name='elevator',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='house',
            name='parking',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='house',
            name='playground',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='house',
            name='security',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='house',
            name='shop',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Standpipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pipes', to='api.section')),
            ],
        ),
    ]
