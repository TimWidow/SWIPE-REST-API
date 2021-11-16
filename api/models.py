from datetime import datetime, timedelta

import jwt
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager

from project import settings
from . import managers
from django.core.mail import send_mail


class CustomAbstractUser(AbstractBaseUser, PermissionsMixin):

    username_validator = UnicodeUsernameValidator()

    email = models.CharField(
        _('email address'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[],
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this app-admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now, null=True)

    objects = managers.CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return str(self.first_name) + str(self.last_name)

    def get_short_name(self):
        return self.first_name

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')


class User(CustomAbstractUser):
    NOTIFY = (
        ('Мне', 'Мне'),
        ('Мне и агенту', 'Мне и агенту'),
        ('Агенту', 'Агенту'),
        ('Отключить', 'Отключить'),

    )
    avatar = models.ImageField('Аватар', upload_to='images/user/', null=True, blank=True)
    subscribe = models.BooleanField(default=False, blank=True)
    subscribe_expired = models.DateTimeField(null=True, blank=True)
    notification = models.CharField(choices=NOTIFY, default=0, max_length=55)
    agent_first_name = models.CharField(max_length=255, null=True, blank=True)
    agent_last_name = models.CharField(max_length=255, null=True, blank=True)
    agent_email = models.EmailField(null=True, blank=True)
    agent_phone = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'api'


class UserManager(BaseUserManager):

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Указанный email пользователя должно быть установлено')

        if not password:
            raise ValueError('Данный пароль должен быть установлен')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class PhoneModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='related_phone')
    Mobile = models.IntegerField(blank=False)
    isVerified = models.BooleanField(blank=False, default=False)
    counter = models.IntegerField(default=0, blank=False)

    def __str__(self):
        return str(self.Mobile)


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField()


class House(models.Model):
    HOUSE_CURRENT_STATUS = (
        ('Сдан', 'Сдан'),
        ('Не сдан', 'Не сдан')
    )
    HOUSE_STATUS = (
        ('Квартиры', 'Квартиры'),
        ('Офис', 'Офис'),
    )
    BUILDING_TECHNOLOGY = (
        ('Монолитный каркас с керамзитом', 'Монолитный каркас с керамзитом'),
        ('Панелька', 'Панелька')
    )
    HOUSE_TYPE = (
        ('Многоквартирный', 'Многоквартирный'),
        ('Частный', 'Частный')
    )
    HOUSE_TERRITORY_TYPE = (
        ('Закрытая, охраняемая', 'Закрытая, охраняемая'),
        ('Открытая', 'Открытая')
    )
    INVOICE_TYPE = (
        ('Платежи', 'Платежи'),
        ('Автоплатеж', 'Автоплатеж')
    )
    HEATING_TYPE = (
        ('Центральное', 'Центральное'),
        ('Личное', 'Личное')
    )
    WATER_TYPE = (
        ('Канализация', 'Канализация'),
        ('Яма', 'Яма')
    )
    address = models.CharField(max_length=255)
    house_status = models.CharField(choices=HOUSE_STATUS, max_length=55)
    building_technologies = models.CharField(choices=BUILDING_TECHNOLOGY, max_length=255)
    house_type = models.CharField(choices=HOUSE_TYPE, max_length=255)
    territory_type = models.CharField(choices=HOUSE_TERRITORY_TYPE, max_length=255)
    current_status = models.CharField(choices=HOUSE_CURRENT_STATUS, max_length=255)
    distance_to_sea = models.FloatField()
    registration_type = models.CharField(max_length=255, verbose_name='Оформление')
    invoice_type = models.CharField(choices=INVOICE_TYPE, max_length=255, verbose_name='Коммунальные платежи')
    invoice_options = models.CharField(max_length=255, verbose_name='Варианты расчёта')
    purpose = models.CharField(max_length=255, verbose_name='Назначение')
    contract_amount = models.CharField(max_length=255, verbose_name='Сумма в договоре')
    manager = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    celling_height = models.FloatField(null=True)
    gas = models.BooleanField(default=False)
    heating = models.CharField(choices=HEATING_TYPE, null=True, max_length=255)
    water = models.CharField(choices=WATER_TYPE, max_length=255)


class Document(models.Model):
    file = models.FileField(upload_to='file/')
    house = models.ForeignKey(House, on_delete=models.CASCADE)


class HouseNews(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок новости')
    description = models.TextField(verbose_name='Описание новости')
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name='ЖК')


class Section(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Секция')


class Floor(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Этаж')

    def __str__(self):
        return self.name


class Promotion(models.Model):
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
        ('Семейное гнездышко', 'Семейное гнездышко'),
        ('Отдельная парковка', 'Отдельная парковка'),
    )

    type = models.CharField(choices=PROMO_TYPE, max_length=255, null=True)
    phrase = models.CharField(choices=PHRASE, max_length=255, verbose_name='Фраза', null=True)
    color = models.CharField(choices=COLOR, max_length=255, null=True)


class Apartment(models.Model):
    DOC_TYPE = (
        ('Документ собственности', 'Документ собственности'),
        ('Доверенность', 'Доверенность')
    )
    APART_TYPE = (
        ('Апартаменты', 'Апартаменты'),
        ('Пентхаус', 'Пентхаус')
    )
    APART_STATUS = (
        ('Черновая отделка', 'Черновая отделка'),
        ('Требует ремонта', 'Требует ремонта'),
        ('Требует капитальный ремонт', 'Требует капитальный ремонт'),
    )
    HEATING_TYPE = (
        ('Газ', 'Газ'),
        ('Дрова', 'Дрова')
    )
    SETTLEMENT_TYPE = (
        ('Мат. капитал', 'Мат. капитал'),
        ('Ипотека', 'Ипотека')
    )
    CONTACT_TYPE = (
        ('Звонок', 'Звонок'),
        ('Звонок + сообщение', 'Звонок + сообщение')
    )
    ADV_TYPE = (
        ('Первичный рынок', 'Первичный рынок'),
        ('Вторичный рынок', 'Вторичный рынок')
    )
    APART_CLASS = (
        ('Студия', 'Студия'),
        ('Студия, санузел', 'Студия, санузел')
    )

    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, null=True, blank=True)
    document = models.CharField(choices=DOC_TYPE, max_length=255)
    room_count = models.IntegerField()
    apartment_type = models.CharField(choices=APART_TYPE, max_length=255)
    apartment_status = models.CharField(choices=APART_STATUS, max_length=255)
    apartment_area = models.FloatField()
    kitchen_area = models.FloatField()
    loggia = models.BooleanField(default=False)
    heating_type = models.CharField(choices=HEATING_TYPE, max_length=255)
    settlement_type = models.CharField(choices=SETTLEMENT_TYPE, max_length=255)
    contact = models.CharField(choices=CONTACT_TYPE, max_length=255)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, null=True, blank=True)
    commission = models.IntegerField()
    description = models.TextField()
    price = models.IntegerField()
    main_image = models.ImageField(upload_to='image/')
    address = models.CharField(max_length=255)
    adv_type = models.CharField(choices=ADV_TYPE, max_length=255)
    apart_class = models.CharField(choices=APART_CLASS, max_length=255)
    is_actual = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владедец объявления', null=True, blank=True)
    created_date = models.DateTimeField(auto_now=True, null=True)


class ApartImgRelations(models.Model):
    apart = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='image/')


class UserApartRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apart = models.ForeignKey(Apartment, on_delete=models.CASCADE)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_sender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_recipient')
    text = models.TextField()
