# Generated by Django 3.2.9 on 2021-12-06 10:10

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='Фамилия')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='UA', unique=True, verbose_name='Телефон')),
                ('verified', models.BooleanField(default=False, verbose_name='Верификация пройдена')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('role', models.CharField(choices=[('USER', 'Клиент'), ('AGENT', 'Агент'), ('NOTARY', 'Нотариус'), ('DEPART', 'Отдел продаж'), ('SYSTEM', 'Администрация Swipe')], default='USER', max_length=6, verbose_name='Роль')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='images/user/', verbose_name='Фото профиля')),
                ('agent_first_name', models.CharField(blank=True, max_length=150, verbose_name='Имя агента')),
                ('agent_last_name', models.CharField(blank=True, max_length=150, verbose_name='Фамилия агента')),
                ('agent_phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region='UA', verbose_name='Телефон агента')),
                ('agent_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email агента')),
                ('subscription_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания подписки')),
                ('notifications', models.CharField(choices=[('ME', 'Мне'), ('MEANDAGENT', 'Мне и агенту'), ('AGENT', 'Агенту'), ('OFF', 'Отключить')], default='ME', max_length=10, verbose_name='Уведомления')),
                ('switch', models.BooleanField(default=False, verbose_name='Переключить звонки и сообщения на агента')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Apartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.CharField(choices=[('OWNERSHIP', 'Документ собственности'), ('POA', 'Доверенность')], max_length=9, verbose_name='Документ')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адрес')),
                ('rooms', models.PositiveSmallIntegerField(verbose_name='Количество комнат')),
                ('apart_type', models.CharField(choices=[('APARTMENT', 'Апартаменты'), ('PENTHOUSE', 'Пентхаус')], max_length=9, verbose_name='Назначение')),
                ('apart_status', models.CharField(choices=[('SHELL', 'Черновая'), ('EURO', 'Евроремонт'), ('REPAIR', 'Требует ремонта'), ('FULL REPAIR', 'Требуется капитальный ремонт')], max_length=11, verbose_name='Жилое состояние')),
                ('apart_layout', models.CharField(choices=[('STUDIO', 'Студия, санузел'), ('GUEST', 'Гостинка'), ('SMALL', 'Малосемейка'), ('ISOLATED', 'Изолированные комнаты'), ('ADJOINING', 'Смежные комнаты'), ('FREE', 'Свободная планировка')], max_length=9, verbose_name='Планировка')),
                ('apart_area', models.FloatField(verbose_name='Общая площадь')),
                ('kitchen_area', models.FloatField(verbose_name='Площадь кухни')),
                ('loggia', models.BooleanField(default=False, verbose_name='Балкон/лоджия')),
                ('heating', models.CharField(choices=[('GAS', 'Газовое'), ('WOOD', 'Дрова')], max_length=4, verbose_name='Отопление')),
                ('payment', models.CharField(choices=[('CAPITAL', 'Мат. капитал'), ('MORTGAGE', 'Ипотека'), ('CAP&MORT', 'Мат. капитал, Ипотека')], max_length=8, verbose_name='Варианты расчёта')),
                ('contact', models.CharField(choices=[('CALL', 'Звонок'), ('MESSAGE', 'Сообщение'), ('CALL&MES', 'Звонок + сообщение')], max_length=12, verbose_name='Способ связи')),
                ('commission', models.FloatField(verbose_name='Комиссия агенту')),
                ('description', models.TextField(verbose_name='Описание')),
                ('price', models.FloatField(verbose_name='Цена')),
                ('is_actual', models.BooleanField(default=False, verbose_name='Актуально')),
                ('created', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('city', models.CharField(max_length=255, verbose_name='Город')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Инфраструктура ЖК')),
                ('property_type', models.CharField(choices=[('SECONDARY', 'Вторичный рынок'), ('NEW', 'Новостройки'), ('COTTAGE', 'Коттедж')], max_length=10, verbose_name='Тип недвижимости')),
                ('house_leased', models.CharField(choices=[('LEASED', 'Сдан'), ('NOT LEASED', 'Не сдан')], max_length=10, verbose_name='Эксплуатация')),
                ('house_status', models.CharField(choices=[('ECO', 'Эконом'), ('COMFORT', 'Комфорт'), ('COMFORT', 'Бизнес'), ('ELITE', 'Элитный')], max_length=10, verbose_name='Статус ЖК')),
                ('house_type', models.CharField(choices=[('MULTI', 'Многоквартирный'), ('PRIVATE', 'Частный')], max_length=10, verbose_name='Вид дома')),
                ('technology', models.CharField(choices=[('MONO', 'Монолитный каркас с керамзитно-блочным заполнением'), ('PANEL', 'Панельный'), ('BRICK', 'Кирпич')], max_length=10, verbose_name='Технология строительства')),
                ('territory', models.CharField(choices=[('CLOSED', 'Закрытая'), ('OPEN', 'Открытая')], max_length=10, verbose_name='Территория')),
                ('sea', models.FloatField(blank=True, null=True, verbose_name='Расстояние до моря')),
                ('ceiling', models.FloatField(blank=True, null=True, verbose_name='Высота потолков')),
                ('gas', models.BooleanField(default=False, verbose_name='Газ')),
                ('electricity', models.BooleanField(default=False, verbose_name='Электричество')),
                ('heating', models.CharField(choices=[('CENTRAL', 'Центральное'), ('PERSONAL', 'Индивидуальное')], max_length=8, null=True, verbose_name='Отопление')),
                ('sewerage', models.CharField(choices=[('CENTRAL', 'Центральная'), ('PIT', 'Яма')], max_length=8, verbose_name='Канализация')),
                ('water', models.CharField(choices=[('SEWERAGE', 'Центральное'), ('AUTO', 'Автономное')], max_length=8, verbose_name='Водоснабжение')),
                ('doc_options', models.CharField(blank=True, max_length=255, null=True, verbose_name='Варианты оформления')),
                ('pay_options', models.CharField(blank=True, max_length=255, null=True, verbose_name='Варианты расчёта')),
                ('status', models.CharField(blank=True, max_length=255, null=True, verbose_name='Статус недвижимости')),
                ('contract_amount', models.CharField(blank=True, max_length=255, null=True, verbose_name='Сумма в договоре')),
                ('playground', models.BooleanField(default=False, verbose_name='Детская площадка')),
                ('parking', models.BooleanField(default=False, verbose_name='Паркинг')),
                ('shop', models.BooleanField(default=False, verbose_name='Супермаркет рядом')),
                ('elevator', models.BooleanField(default=False, verbose_name='Скоростной лифт')),
                ('security', models.BooleanField(default=False, verbose_name='Охрана')),
            ],
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Большое объявление', 'Большое объявление'), ('Поднять объявление', 'Поднять объявление'), ('Турбо', 'Турбо')], max_length=255, null=True, verbose_name='Тип')),
                ('phrase', models.CharField(choices=[('Подарок при покупке', 'Подарок при покупке'), ('Возможен торг', 'Возможен торг'), ('Квартира у моря', 'Квартира у моря'), ('В спальном районе', 'В спальном районе'), ('Вам повезло с ценой', 'Вам повезло с ценой'), ('Для большой семьи', 'Для большой семьи'), ('Семейное гнёздышко', 'Семейное гнёздышко'), ('Отдельная парковка', 'Отдельная парковка')], max_length=255, null=True, verbose_name='Фраза')),
                ('color', models.CharField(choices=[('Красный', 'Красный'), ('Зелёный', 'Зелёный'), ('Синий', 'Синий'), ('Желтый', 'Желтый')], max_length=255, null=True, verbose_name='Цвет')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(verbose_name='Секция')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.house')),
            ],
        ),
        migrations.CreateModel(
            name='UserApart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('apart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.apartment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Standpipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pipes', to='api.section')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HouseNew',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок новости')),
                ('description', models.TextField(verbose_name='Описание новости')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.house', verbose_name='ЖК')),
            ],
        ),
        migrations.CreateModel(
            name='HouseImg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='houses/', verbose_name='Фото')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.house', verbose_name='ЖК')),
            ],
        ),
        migrations.CreateModel(
            name='HouseDoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='documents/', verbose_name='Файл')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.house', verbose_name='ЖК')),
            ],
        ),
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(verbose_name='Этаж')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.section')),
            ],
        ),
        migrations.AddField(
            model_name='apartment',
            name='floor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.floor', verbose_name='Этаж'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='house',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.house', verbose_name='ЖК'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец объявления'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='promotion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.promotion', verbose_name='Продвижение'),
        ),
        migrations.CreateModel(
            name='ApartImg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='apartments/', verbose_name='Фото')),
                ('apart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.apartment', verbose_name='Квартира')),
            ],
        ),
    ]
