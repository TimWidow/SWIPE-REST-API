from datetime import datetime, timedelta
import jwt
from django.apps import apps
from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied
from django.db.models import *
from phonenumber_field.modelfields import PhoneNumberField
from swipe import settings


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given phone, email, and password.
        """
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


# A few helper functions for common logic between User and AnonymousUser.
def _user_get_permissions(user, obj, from_name):
    permissions = set()
    name = 'get_%s_permissions' % from_name
    for backend in auth.get_backends():
        if hasattr(backend, name):
            permissions.update(getattr(backend, name)(user, obj))
    return permissions


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', ]
    objects = UserManager()

    NOTIFY = (
        ('ME', 'Мне'),
        ('MEANDAGENT', 'Мне и агенту'),
        ('AGENT', 'Агенту'),
        ('OFF', 'Отключить')
    )
    ROLES = (
        ('USER', 'Клиент'),
        ('AGENT', 'Агент'),
        ('NOTARY', 'Нотариус'),
        ('DEPART', 'Отдел продаж'),
        ('SYSTEM', 'Администрация Swipe')
    )
    username = None
    first_name = CharField(max_length=150, blank=True, verbose_name='Имя')
    last_name = CharField(max_length=150, blank=True, verbose_name='Фамилия')
    phone = PhoneNumberField(unique=True, region='UA', verbose_name='Телефон')
    verified = BooleanField(default=False, verbose_name='Верификация пройдена')
    email = EmailField(unique=True, verbose_name='Email')
    role = CharField(max_length=6, choices=ROLES, default='USER', verbose_name='Роль')
    avatar = ImageField(upload_to='images/user/', blank=True, null=True, verbose_name='Фото профиля')
    agent_first_name = CharField(max_length=150, blank=True, verbose_name='Имя агента')
    agent_last_name = CharField(max_length=150, blank=True, verbose_name='Фамилия агента')
    agent_phone = PhoneNumberField(region='UA', blank=True, null=True, verbose_name='Телефон агента')
    agent_email = EmailField(blank=True, null=True, verbose_name='Email агента')
    subscription_date = DateTimeField(blank=True, null=True, verbose_name='Дата окончания подписки')
    notifications = CharField(max_length=10, choices=NOTIFY, default='ME', verbose_name='Уведомления')
    switch = BooleanField(default=False, verbose_name='Переключить звонки и сообщения на агента')

    @property
    def token(self):
        return self._generate_jwt_token()

    # def authenticate(self, otp):
    #    """ This method authenticates the given otp"""
    # Here we are using Time Based OTP. The interval is 300 seconds.
    # otp must be provided within this interval or it's invalid
    #    token = pyotp.TOTP(self.key, interval=300)
    #    return token.verify(otp)

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    class Meta:
        app_label = 'api'


class House(Model):
    PROPERTY_TYPE = (
        ('SECONDARY', 'Вторичный рынок'),
        ('NEW', 'Новостройки'),
        ('COTTAGE', 'Коттедж'),
    )
    HOUSE_LEASED = (
        ('LEASED', 'Сдан'),
        ('NOT LEASED', 'Не сдан')
    )
    HOUSE_STATUS = (
        ('ECO', 'Эконом'),
        ('COMFORT', 'Комфорт'),
        ('COMFORT', 'Бизнес'),
        ('ELITE', 'Элитный'),
    )
    HOUSE_TYPE = (
        ('MULTI', 'Многоквартирный'),
        ('PRIVATE', 'Частный')
    )
    TECHNOLOGY = (
        ('MONO', 'Монолитный каркас с керамзитно-блочным заполнением'),
        ('PANEL', 'Панельный'),
        ('BRICK', 'Кирпич')
    )

    TERRITORY = (
        ('CLOSED', 'Закрытая'),
        ('OPEN', 'Открытая')
    )
    HEATING = (
        ('CENTRAL', 'Центральное'),
        ('PERSONAL', 'Индивидуальное')
    )
    SEWERAGE = (
        ('CENTRAL', 'Центральная'),
        ('PIT', 'Яма')
    )
    WATER = (
        ('SEWERAGE', 'Центральное'),
        ('AUTO', 'Автономное')
    )
    title = CharField(max_length=255, verbose_name='Название')
    city = CharField(max_length=255, verbose_name='Город')
    address = CharField(max_length=255, verbose_name='Адрес')
    description = TextField(blank=True, null=True, verbose_name='Инфраструктура ЖК')
    property_type = CharField(max_length=10, choices=PROPERTY_TYPE, verbose_name='Тип недвижимости')
    house_leased = CharField(max_length=10, choices=HOUSE_LEASED, verbose_name='Эксплуатация')
    house_status = CharField(max_length=10, choices=HOUSE_STATUS, verbose_name='Статус ЖК')
    house_type = CharField(max_length=10, choices=HOUSE_TYPE, verbose_name='Вид дома')
    technology = CharField(max_length=10, choices=TECHNOLOGY, verbose_name='Технология строительства')
    territory = CharField(max_length=10, choices=TERRITORY, verbose_name='Территория')
    sea = FloatField(verbose_name='Расстояние до моря', blank=True, null=True)
    ceiling = FloatField(verbose_name='Высота потолков', blank=True, null=True)
    gas = BooleanField(default=False, verbose_name='Газ')
    electricity = BooleanField(default=False, verbose_name='Электричество')
    heating = CharField(max_length=8, choices=HEATING, null=True, verbose_name='Отопление')
    sewerage = CharField(max_length=8, choices=SEWERAGE, verbose_name='Канализация')
    water = CharField(max_length=8, choices=WATER, verbose_name='Водоснабжение')
    doc_options = CharField(max_length=255, blank=True, null=True, verbose_name='Варианты оформления')
    pay_options = CharField(max_length=255, blank=True, null=True, verbose_name='Варианты расчёта')
    status = CharField(max_length=255, blank=True, null=True, verbose_name='Статус недвижимости')
    contract_amount = CharField(max_length=255, blank=True, null=True, verbose_name='Сумма в договоре')
    # Benefits
    playground = BooleanField(default=False, verbose_name='Детская площадка')
    parking = BooleanField(default=False, verbose_name='Паркинг')
    shop = BooleanField(default=False, verbose_name='Супермаркет рядом')
    elevator = BooleanField(default=False, verbose_name='Скоростной лифт')
    security = BooleanField(default=False, verbose_name='Охрана')

    def get_next(self, house):
        objects = self.objects.filter(house=house)
        if objects:
            last = objects.last().id
            return last + 1
        return 1

    def __str__(self):
        return self.title


class HouseDoc(Model):
    house = ForeignKey(House, on_delete=CASCADE, verbose_name='ЖК')
    file = FileField(upload_to='documents/', verbose_name='Файл')

    def __str__(self):
        return str(self.house)


class HouseNew(Model):
    house = ForeignKey(House, on_delete=CASCADE, verbose_name='ЖК')
    title = CharField(max_length=255, verbose_name='Заголовок новости')
    description = TextField(verbose_name='Описание новости')

    def __str__(self):
        return str(self.house) + ', ' + str(self.title)


class Section(Model):
    house = ForeignKey(House, on_delete=CASCADE)
    number = PositiveSmallIntegerField(verbose_name='Секция')

    @classmethod
    def get_next(cls, house: House):
        objects = cls.objects.filter(house=house)
        if objects:
            last = objects.last().number
            return last + 1
        return 1

    def __str__(self):
        return str(self.house) + ', Секция ' + str(self.number)


class Floor(Model):
    section = ForeignKey(Section, on_delete=CASCADE)
    number = PositiveSmallIntegerField(verbose_name='Этаж')

    @classmethod
    def get_next(cls, section: Section):
        objects = cls.objects.filter(section=section)
        if objects:
            last = objects.last().number
            return last + 1
        return 1

    def __str__(self):
        return str(self.section) + ', Этаж ' + str(self.number)


class Standpipe(Model):
    name = CharField(max_length=50)
    section = ForeignKey(Section, related_name='pipes', on_delete=CASCADE)


class Promotion(Model):
    PROMO_TYPE = (
        ('Большое объявление', 'Большое объявление'),
        ('Поднять объявление', 'Поднять объявление'),
        ('Турбо', 'Турбо'),
    )
    COLOR = (
        ('Красный', 'Красный'),
        ('Зелёный', 'Зелёный'),
        ('Синий', 'Синий'),
        ('Желтый', 'Желтый'),
    )
    PHRASE = (
        ('Подарок при покупке', 'Подарок при покупке'),
        ('Возможен торг', 'Возможен торг'),
        ('Квартира у моря', 'Квартира у моря'),
        ('В спальном районе', 'В спальном районе'),
        ('Вам повезло с ценой', 'Вам повезло с ценой'),
        ('Для большой семьи', 'Для большой семьи'),
        ('Семейное гнёздышко', 'Семейное гнёздышко'),
        ('Отдельная парковка', 'Отдельная парковка'),
    )

    type = CharField(choices=PROMO_TYPE, max_length=255, null=True, verbose_name='Тип')
    phrase = CharField(choices=PHRASE, max_length=255, null=True, verbose_name='Фраза')
    color = CharField(choices=COLOR, max_length=255, null=True, verbose_name='Цвет')

    def __str__(self):
        return str(self.type) + ' , ' + str(self.phrase) + ' , ' + str(self.color)


class Apartment(Model):
    DOC_TYPE = (
        ('OWNERSHIP', 'Документ собственности'),
        ('POA', 'Доверенность')
    )
    APART_TYPE = (
        ('APARTMENT', 'Апартаменты'),
        ('PENTHOUSE', 'Пентхаус')
    )
    APART_STATUS = (
        ('SHELL', 'Черновая'),
        ('EURO', 'Евроремонт'),
        ('REPAIR', 'Требует ремонта'),
        ('FULL REPAIR', 'Требуется капитальный ремонт'),
    )
    APART_LAYOUT = (
        ('STUDIO', 'Студия, санузел'),
        ('GUEST', 'Гостинка'),
        ('SMALL', 'Малосемейка'),
        ('ISOLATED', 'Изолированные комнаты'),
        ('ADJOINING', 'Смежные комнаты'),
        ('FREE', 'Свободная планировка'),
    )
    HEATING_TYPE = (
        ('GAS', 'Газовое'),
        ('WOOD', 'Дрова')
    )
    PAY_TYPE = (
        ('CAPITAL', 'Мат. капитал'),
        ('MORTGAGE', 'Ипотека'),
        ('CAP&MORT', 'Мат. капитал, Ипотека'),
    )
    CONTACT_TYPE = (
        ('CALL', 'Звонок'),
        ('MESSAGE', 'Сообщение'),
        ('CALL&MES', 'Звонок + сообщение')
    )

    house = ForeignKey(House, on_delete=CASCADE, null=True, verbose_name='ЖК')
    floor = ForeignKey(Floor, on_delete=CASCADE, blank=True, null=True, verbose_name='Этаж')
    document = CharField(max_length=9, choices=DOC_TYPE, verbose_name='Документ')
    address = CharField(max_length=255, blank=True, null=True, verbose_name='Адрес')
    rooms = PositiveSmallIntegerField(verbose_name='Количество комнат')
    apart_type = CharField(max_length=9, choices=APART_TYPE, verbose_name='Назначение')
    apart_status = CharField(max_length=11, choices=APART_STATUS, verbose_name='Жилое состояние')
    apart_layout = CharField(max_length=9, choices=APART_LAYOUT, verbose_name='Планировка')
    apart_area = FloatField(verbose_name='Общая площадь')
    kitchen_area = FloatField(verbose_name='Площадь кухни')
    loggia = BooleanField(default=False, verbose_name='Балкон/лоджия')
    heating = CharField(max_length=4, choices=HEATING_TYPE, verbose_name='Отопление')
    payment = CharField(max_length=8, choices=PAY_TYPE, verbose_name='Варианты расчёта')
    contact = CharField(max_length=12, choices=CONTACT_TYPE, verbose_name='Способ связи')
    promotion = ForeignKey(Promotion, on_delete=CASCADE, blank=True, null=True, verbose_name='Продвижение')
    commission = FloatField(verbose_name='Комиссия агенту')
    description = TextField(verbose_name='Описание')
    price = FloatField(verbose_name='Цена')
    is_actual = BooleanField(default=False, verbose_name='Актуально')
    owner = ForeignKey(User, on_delete=CASCADE, blank=True, null=True, verbose_name='Владелец объявления')
    created = DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.floor)

    class Meta:
        ordering = ['-created']


class HouseImg(Model):
    house = ForeignKey(House, on_delete=CASCADE, verbose_name='ЖК')
    image = ImageField(upload_to='houses/', verbose_name='Фото')

    def __str__(self):
        return str(self.house)


class ApartImg(Model):
    apart = ForeignKey(Apartment, on_delete=CASCADE, verbose_name='Квартира')
    image = ImageField(upload_to='apartments/', verbose_name='Фото')

    def __str__(self):
        return str(self.apart)


class UserApart(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    apart = ForeignKey(Apartment, on_delete=CASCADE)


class Message(Model):
    sender = ForeignKey(User, on_delete=CASCADE, related_name='sender')
    recipient = ForeignKey(User, on_delete=CASCADE, related_name='recipient')
    text = TextField()
