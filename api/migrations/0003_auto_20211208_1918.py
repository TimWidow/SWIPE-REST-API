# Generated by Django 3.2.9 on 2021-12-08 17:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_user_managers'),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(verbose_name='Корпус')),
            ],
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(choices=[('PRICE', 'Некорректная цена'), ('PHOTO', 'Некорректное фото'), ('DESC', 'Некорректное описание'), ('ANY', 'Другое')], max_length=5)),
                ('description', models.TextField(blank=True, null=True)),
                ('rejected', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment', models.CharField(choices=[('CAPITAL', 'Мат. капитал'), ('MORTGAGE', 'Ипотека'), ('CAP&MORT', 'Мат. капитал, Ипотека')], max_length=8, verbose_name='Варианты расчёта')),
                ('contact', models.CharField(choices=[('CALL', 'Звонок'), ('MESSAGE', 'Сообщение'), ('CALL&MES', 'Звонок + сообщение')], max_length=12, verbose_name='Способ связи')),
                ('commission', models.FloatField(verbose_name='Комиссия агенту')),
                ('description', models.TextField(verbose_name='Описание')),
                ('price', models.FloatField(verbose_name='Цена')),
                ('is_actual', models.BooleanField(default=False, verbose_name='Актуально')),
                ('created', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата создания')),
                ('rejected', models.BooleanField(default=False, verbose_name='Отклонено')),
            ],
        ),
        migrations.CreateModel(
            name='PostImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='posts/')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.post')),
            ],
        ),
        migrations.CreateModel(
            name='RequestToChess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterModelOptions(
            name='apartment',
            options={'ordering': ['-id']},
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='commission',
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='contact',
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='created',
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='description',
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='is_actual',
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='payment',
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='price',
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='promotion',
        ),
        migrations.RemoveField(
            model_name='section',
            name='house',
        ),
        migrations.RemoveField(
            model_name='standpipe',
            name='name',
        ),
        migrations.AddField(
            model_name='apartment',
            name='booked',
            field=models.BooleanField(default=False, verbose_name='Забронирована'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Клиент'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='owned',
            field=models.BooleanField(default=False, verbose_name='Выкуплена'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.section', verbose_name='Секция'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='standpipe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.standpipe', verbose_name='Стояк'),
        ),
        migrations.AddField(
            model_name='house',
            name='sales_department',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, related_name='managed_houses', to='api.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='standpipe',
            name='number',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Стояк'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='standpipe',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.section'),
        ),
        migrations.DeleteModel(
            name='UserApart',
        ),
        migrations.AddField(
            model_name='requesttochess',
            name='apart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.apartment'),
        ),
        migrations.AddField(
            model_name='requesttochess',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.house'),
        ),
        migrations.AddField(
            model_name='post',
            name='apart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='api.apartment', verbose_name='Квартира'),
        ),
        migrations.AddField(
            model_name='post',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='api.house', verbose_name='ЖК'),
        ),
        migrations.AddField(
            model_name='post',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Apart_Owner', to=settings.AUTH_USER_MODEL, verbose_name='Владелец объявления'),
        ),
        migrations.AddField(
            model_name='post',
            name='promotion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.promotion', verbose_name='Продвижение'),
        ),
        migrations.AddField(
            model_name='post',
            name='reject_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Post_complaint', to='api.complaint', verbose_name='Жалоба'),
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.post'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='block',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.house'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='block',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.block', verbose_name='Корпус'),
        ),
        migrations.AddField(
            model_name='section',
            name='block',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.block'),
            preserve_default=False,
        ),
    ]
